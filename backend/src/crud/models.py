from typing import List

from sqlalchemy import (
    Column, String, TIMESTAMP,
    func, DateTime, Float, ForeignKey, Boolean, Date,
    UniqueConstraint
)
from sqlalchemy.dialects.mysql.types import BIT, INTEGER
from sqlalchemy.orm import relationship, Mapped

from src.crud.engine import Base


_COLLATION = "utf8mb4_general_ci"


class CityRecord(Base):
    __tablename__ = "cities"
    city_id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    city_name = Column(
        String(50, collation=_COLLATION),
        unique=True
    )


class PersonTypeRecord(Base):
    __tablename__ = "person_types"
    person_type_id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    person_type = Column(
        String(20, collation=_COLLATION),
        unique=True,
        nullable=False,
    )
    discount_amount = Column(
        Float(),
        nullable=False,
    )


class PermissionsRecord(Base):
    __tablename__ = "permissions"
    permission_id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    permission = Column(
        String(20, collation=_COLLATION),
        unique=True,
        nullable=False,
    )
    roles: Mapped[List["RolePermissionsRecord"]] = relationship(
        "RolePermissionsRecord", back_populates="role_permission"
    )


class HallsRecord(Base):
    __tablename__ = "halls"
    hall_id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    hall_name = Column(
        String(50, collation=_COLLATION),
        nullable=False,
    )
    seats_per_row = Column(
        INTEGER(unsigned=True),
        nullable=False,
    )
    no_of_rows = Column(
        INTEGER(unsigned=True),
        nullable=False,
    )


class RolePermissionsRecord(Base):
    __tablename__ = "role_permissions"
    id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    role_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("roles.role_id"),
        nullable=False,
    )
    permissions_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("permissions.permission_id"),
        nullable=False,
    )
    role: Mapped[List["RolesRecord"]] = relationship(
        "RolesRecord", back_populates="permissions"
    )
    role_permission: Mapped["PermissionsRecord"] = relationship(
        "PermissionsRecord", back_populates="roles"
    )
    __table_args__ = (
        UniqueConstraint(
            'role_id', 'permissions_id', name='_role-permission'
        ),
    )


class RolesRecord(Base):
    __tablename__ = "roles"
    role_id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    role_name = Column(
        String(20, collation=_COLLATION),
        unique=True,
        nullable=False,
    )
    permissions: Mapped[List["RolePermissionsRecord"]] = relationship(
        "RolePermissionsRecord", back_populates="role", uselist=True
    )
    user_roles: Mapped[List["UserRolesRecord"]] = relationship(
        "UserRolesRecord", back_populates="role"
    )


class UserRolesRecord(Base):
    __tablename__ = "user_roles"
    id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    role_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("roles.role_id"),
        nullable=False,
    )
    user_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("users.user_id"),
        nullable=False,
    )
    __table_args__ = (
        UniqueConstraint(
            'role_id', 'user_id', name='_user-roles'
        ),
    )
    # user: Mapped["UserRecord"] = relationship(
    #     "UserRecord", "roles_user"
    # )
    role: Mapped["RolesRecord"] = relationship(
        "RolesRecord", back_populates="user_roles"
    )


class UsersRecord(Base):
    __tablename__ = "users"
    user_id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    name = Column(
        String(50, collation=_COLLATION),
        nullable=False,
    )
    email = Column(
        String(50, collation=_COLLATION),
        nullable=False,
    )
    password = Column(
        String(60, collation=_COLLATION),
        nullable=False,
    )
    # user_roles: Mapped[List["UserRolesRecord"]] = relationship(
    #     "UserRolesRecord", back_populates="user_permissions"
    # )


# class RolePermissionsRecord(Base):
#     __tablename__ = "role_permissions"
#     id = Column(
#         INTEGER(unsigned=True),
#         primary_key=True,
#         autoincrement=True,
#         nullable=False,
#         unique=True,
#     )
#     role_id = Column(
#         INTEGER(unsigned=True),
#         ForeignKey("roles.id"),
#         nullable=False,
#     )
#     permissions_id = Column(
#         INTEGER(unsigned=True),
#         ForeignKey("permissions.id"),
#         nullable=False,
#     )
#     role = relationship("RolesRecord", back_populates="role_permissions")
#     # role =

# class FilmImagesRecord:
#     __tablename__ = "film_images"
#     person_type_id = Column(
#         INTEGER(unsigned=True),
#         primary_key=True,
#         autoincrement=True,
#         nullable=False,
#         unique=True,
#     )
#     film_id: Column
