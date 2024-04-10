from collections import defaultdict
from typing import List

from src.crud.models import UsersRecord
from src.schema.users import User, Role, Permission


class UserFactory:
    @staticmethod
    def create_full_user(mp: dict) -> User:
        user_record = mp["user"]
        roles_records = mp["roles"]
        permissions_records = mp["permissions"]
        user_roles_records = mp["user_roles"]
        role_permissions_records = mp["role_permissions"]

        roles_permissions = defaultdict(list)
        _permissions = []
        roles = []

        for rp_id, role_permissions_record in role_permissions_records.items():
            permissions_record = permissions_records[
                role_permissions_record.permissions_id
            ]

            roles_permissions[
                role_permissions_record.role_id
            ].append(permissions_record)

            _permissions.append(permissions_record.permission)

        for role_id, role_record in roles_records.items():
            permissions = [
                Permission(
                    id=x.permission_id,
                    name=x.permission
                ) for x in roles_permissions[role_id]
            ]
            roles.append(
                Role(
                    id=role_id,
                    name=role_record.role_name,
                    permissions=permissions
                )
            )

        user = UserFactory.create_half_user(user_record)

        user.permissions = set(_permissions)
        user.roles = roles

        return user

    @staticmethod
    def create_half_user(user_record: UsersRecord) -> User:
        return User(
            id=user_record.user_id,
            name=user_record.name,
            email=user_record.email,
            password=user_record.password,
            status=user_record.status,
        )

    @staticmethod
    def create_half_users(user_records) -> List[User]:
        return [
            UserFactory.create_half_user(x) for x in user_records
        ]
