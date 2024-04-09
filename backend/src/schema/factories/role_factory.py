from collections import defaultdict

from src.schema.users import Role, Permission


class RoleFactory:
    @staticmethod
    def get_roles(_map: dict):
        roles_records = _map["roles"]
        permissions_records = _map["permissions"]
        role_permissions_records = _map["role_permissions"]

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

        return roles
