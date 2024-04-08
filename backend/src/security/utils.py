from fastapi import HTTPException
from typing import List, Set
from starlette import status


def check_scope(
        user_scopes: Set[str],
        server_scopes: List[str],
        auth_value: str
) -> None:
    for scope in server_scopes:
        if scope not in user_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": auth_value},
            )
