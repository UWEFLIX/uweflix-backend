from datetime import timedelta, datetime
from typing import Annotated
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt, JWTError  # from package python-jose
from passlib.context import CryptContext
from starlette import status
from src.crud.queries.user import select_user_by_email
from src.schema.users import User
from src.schema.security import TokenData
from src.schema.factories.user_factory import UserFactory
from src.security.one_time_passwords import OTP
from src.security.utils import check_scope
from cryptography.fernet import Fernet
import os

from src.utils.mailing import EmailClient

# change with: ```openssl rand -hex 32```
SECRET_KEY = os.getenv("OAUTH2_SECRET")
ENCRYPTION_KEY = os.getenv("ENCRYPTION_SECRET")  # Fernet.generate_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRE_MINUTES"))
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
EMAILS = EmailClient(
    server=os.getenv("MAILING_SERVER"),
    port=os.getenv("SMTP_PORT"),
    username=os.getenv("MAILING_USERNAME"),
    password=os.getenv("MAILING_PASSWORD"),
)
fernet = Fernet(ENCRYPTION_KEY)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
)
otp = OTP(os.environ.get("OTP_SECRET"))


def verify_password(plain_password: str, hashed_password: str):
    """
        Verify the password
        :param: plain_password
        :param: hashed password
        :return: boolean, true if correct
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def validate_token(
        token: str,
        exception: HTTPException,
) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        password: str = payload.get("password")

        if username is None:
            raise exception
        token_data = TokenData(
            username=username,
            password=password,
        )
    except JWTError:
        raise exception

    return token_data


async def authenticate_user(
        username: str, password: str
) -> dict | bool:
    user = await select_user_by_email(username)
    if not user:
        return False
    if not verify_password(password, user["user"].password):
        return False
    return user


def create_access_token(
        data: dict, expires_delta: timedelta | None = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(days=150)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        security_scopes: SecurityScopes
) -> User:
    if security_scopes.scopes:
        authenticate_value = (
            f'Bearer scope="{security_scopes.scope_str}"'
        )
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    token_data = validate_token(
        token, credentials_exception
    )

    data = await select_user_by_email(username=token_data.username)

    if not data:
        raise credentials_exception

    user = UserFactory.create_full_user(data)

    # check_scope(
    #     user.permissions,
    #     security_scopes.scopes,
    #     authenticate_value
    # )

    return user


async def get_current_active_user(
    current_user: Annotated[
        User, Security(get_current_user, scopes=[])
    ]
):
    if current_user.status != "ENABLED":
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def validate_token_password(
        token_data: TokenData, db_password: str, exception
) -> None:
    token_password: str = token_data.password
    if token_password is None:
        raise exception

    decrypted_password = fernet.decrypt(token_password).decode()
    if decrypted_password != db_password:
        raise exception
