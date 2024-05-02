from datetime import timedelta
from typing import Annotated

from fastapi import FastAPI, Depends, Security, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.middleware.cors import CORSMiddleware

from src.schema.factories.user_factory import UserFactory
from src.schema.security import Token
from src.schema.users import User
from src.security.security import (
    get_current_active_user, authenticate_user, fernet,
    ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
)
from src.utils.utils import lifespan

from src.endpoints.accounts.accounts import router as accounts
from src.endpoints.clubs.clubs import router as clubs
from src.endpoints.users.users import router as users
from src.endpoints.bookings.bookings import router as bookings
from src.endpoints.films.films import router as films

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List your allowed origins here
    allow_credentials=True,
    allow_methods=["*"],  # You can restrict the HTTP methods if needed
    allow_headers=["*"],  # You can restrict the headers if needed
)

app.include_router(clubs)
app.include_router(users)
app.include_router(bookings)
app.include_router(accounts)
app.include_router(films)


@app.post(
    "/token", response_model=Token, tags=["Users"],
    status_code=201
)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    Create a token up to specification of Oauth2 Scope Authentication
    db tables are checked to see if the user should have those modules
    """
    user_data = await authenticate_user(
        form_data.username, form_data.password
    )

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = UserFactory.create_full_user(user_data)
    if user.status != "ENABLED":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scopes = user.permissions
    if len(scopes) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No scopes",
            headers={"WWW-Authenticate": "Bearer"},
        )

    encrypted_password = fernet.encrypt(user.password.encode()).decode()

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "scopes": list(scopes),
            "password": encrypted_password
        },
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get(
    "/users/me", response_model=User, tags=["Users"],
)
async def read_users_me(
        current_user: Annotated[
            User, Security(get_current_active_user, scopes=[])
        ]
):
    return current_user

