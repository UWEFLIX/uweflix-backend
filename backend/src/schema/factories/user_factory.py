from collections import defaultdict

from src.schema.users import User, Role, Permission


class UserFactory:
    @staticmethod
    def create_full_user(mp: dict):
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

        return User(
            id=user_record.user_id,
            email=user_record.email,
            name=user_record.name,
            password=user_record.password,
            permissions=set(_permissions),
            roles=roles,
            status=user_record.status
        )
