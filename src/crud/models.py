from sqlalchemy import (
    Column, String, DateTime, Float, ForeignKey,
    UniqueConstraint, Enum, Text, text, func, CheckConstraint
)
from sqlalchemy.dialects.mysql.types import BIT, INTEGER
from src.crud.engine import Base

_COLLATION = "utf8mb4_general_ci"


class CitiesRecord(Base):
    __tablename__ = "city"
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


class PermissionsRecord(Base):
    __tablename__ = "permission"
    permission_id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    permission = Column(
        String(50, collation=_COLLATION),
        unique=True,
        nullable=False,
    )
    # roles: Mapped[List["RolePermissionsRecord"]] = relationship(
    #     "RolePermissionsRecord", back_populates="role_permission"
    # )


class HallsRecord(Base):
    __tablename__ = "hall"
    hall_id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    hall_name = Column(
        String(50, collation=_COLLATION),
        nullable=False, unique=True
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
    __tablename__ = "role_permission"
    id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    role_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("role.role_id", ondelete="CASCADE"),
        nullable=False,
    )
    permissions_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("permission.permission_id"),
        nullable=False,
    )
    # role: Mapped[List["RolesRecord"]] = relationship(
    #     "RolesRecord", back_populates="permissions"
    # )
    # role_permission: Mapped["PermissionsRecord"] = relationship(
    #     "PermissionsRecord", back_populates="roles"
    # )
    __table_args__ = (
        UniqueConstraint(
            'role_id', 'permissions_id', name='_role-permission'
        ),
    )


class RolesRecord(Base):
    __tablename__ = "role"
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
    # permissions: Mapped[List["RolePermissionsRecord"]] = relationship(
    #     "RolePermissionsRecord", back_populates="role", uselist=True
    # )
    # user_roles: Mapped[List["UserRolesRecord"]] = relationship(
    #     "UserRolesRecord", back_populates="role"
    # )


class UserRolesRecord(Base):
    __tablename__ = "user_role"
    id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    role_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("role.role_id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("user.user_id", ondelete="CASCADE"),
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
    # role: Mapped["RolesRecord"] = relationship(
    #     "RolesRecord", back_populates="user_roles"
    # )


class UsersRecord(Base):
    __tablename__ = "user"
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
        nullable=False, unique=True
    )
    password = Column(
        String(60, collation=_COLLATION),
        nullable=False,
        default="$2b$12$9/pllRXci8nUSKQGZXyrxeSLZUK9CD8whlRURn0ZXsh0m2uA8LzVG"
    )
    status = Column(
        Enum("ENABLED", "DISABLED", name="status", collation=_COLLATION),
        nullable=False, default="ENABLED"
    )
    # user_roles: Mapped[List["UserRolesRecord"]] = relationship(
    #     "UserRolesRecord", back_populates="user_permissions"
    # )


class CardsRecord(Base):
    __tablename__ = "card"
    card_id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    account_id = Column(
        INTEGER(unsigned=True),
        nullable=False,
    )
    card_number = Column(
        String(100, collation=_COLLATION),
        nullable=False
    )
    holder_name = Column(
        String(100, collation=_COLLATION),
        nullable=False
    )
    exp_date = Column(
        String(100, collation=_COLLATION),
        nullable=False
    )
    status = Column(
        Enum(
            "ENABLED", "DISABLED", collation=_COLLATION,
            # native_enum=False
        ),
        nullable=False, default="ENABLED"
    )

    # __table_args__ = (
    #     UniqueConstraint(
    #         'account_id',
    #         name='_account-card'
    #     ),
    # )


class ClubsRecord(Base):
    __tablename__ = "club"
    id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    leader = Column(
        INTEGER(unsigned=True),
        ForeignKey("user.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    club_name = Column(
        String(50, collation=_COLLATION),
        nullable=False,
        unique=True
    )
    addr_street_number = Column(
        String(50, collation=_COLLATION),
        nullable=False,
    )
    addr_street_name = Column(
        String(50, collation=_COLLATION),
        nullable=False,
    )
    post_code = Column(
        INTEGER(unsigned=True),
        nullable=False,
    )
    city_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("city.city_id", ondelete="CASCADE"),
        nullable=False,
    )
    contact_number = Column(
        String(50, collation=_COLLATION),
        nullable=False,
    )
    landline_number = Column(
        String(50, collation=_COLLATION),
        nullable=False,
    )
    email = Column(
        String(50, collation=_COLLATION),
        nullable=False, unique=True
    )
    status = Column(
        Enum("ENABLED", "DISABLED", name="status", collation=_COLLATION),
        nullable=False, default="ENABLED"
    )


class AccountsRecord(Base):
    __tablename__ = "account"
    id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    account_uid = Column(
        String(50, collation=_COLLATION),
        nullable=False,
        unique=True
    )
    name = Column(
        String(50, collation=_COLLATION),
        nullable=False,
    )
    entity_type = Column(
        Enum("USER", "CLUB", name="entity_type", collation=_COLLATION),
        nullable=False,
    )
    entity_id = Column(
        INTEGER(unsigned=True),
        nullable=False,
    )
    discount_rate = Column(
        INTEGER(unsigned=True),
        nullable=False,
    )
    status = Column(
        Enum(
            "ENABLED", "DISABLED", "REQUESTED", "REJECTED",
            collation=_COLLATION
        ),
        nullable=False,
    )
    balance = Column(
        Float, default=0, nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            'entity_type', 'entity_id', "name",
            name='_entity-name'
        ),
        CheckConstraint('balance >= -100', name='balance_constraint')
    )


class ClubMembersRecords(Base):
    __tablename__ = "club_member"
    id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    member = Column(
        INTEGER(unsigned=True),
        ForeignKey("user.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    club = Column(
        INTEGER(unsigned=True),
        ForeignKey("club.id", ondelete="CASCADE"),
        nullable=False,
    )


class PersonTypesRecord(Base):
    __tablename__ = "person_type"
    person_type_id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    person_type = Column(
        String(50, collation=_COLLATION),
        nullable=False, unique=True
    )
    discount_amount = Column(
        INTEGER(unsigned=True), nullable=False
    )


class FilmsRecord(Base):
    __tablename__ = "film"
    film_id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    title = Column(
        String(50, collation=_COLLATION),
        nullable=False,
        unique=True
    )
    age_rating = Column(
        Enum("ADULT", "CHILD", collation=_COLLATION),
        nullable=False,
    )
    duration_sec = Column(
        INTEGER(unsigned=True),
        nullable=False
    )
    trailer_desc = Column(
        Text(500),
        nullable=False
    )
    on_air_from = Column(
        DateTime, nullable=False
    )
    on_air_to = Column(
        DateTime, nullable=False
    )
    is_active = Column(
        BIT(1), nullable=False, default=b'0'
    )
    # poster_image = Column(
    #     String(60, collation=_COLLATION),
    #     nullable=False,
    #     unique=True
    # )


class FilmImagesRecord(Base):
    __tablename__ = "film_image"
    image_id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    film_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("film.film_id", ondelete="CASCADE"),
        nullable=False,
    )
    filename = Column(
        String(50, collation=_COLLATION),
        nullable=False, unique=True, default=text("generate_filename()")
    )
    batch = Column(
        INTEGER,
        nullable=False
    )


class SchedulesRecord(Base):
    __tablename__ = "schedule"
    schedule_id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    hall_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("hall.hall_id", ondelete="CASCADE"),
        nullable=False,
    )
    film_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("film.film_id", ondelete="CASCADE"),
        nullable=False,
    )
    show_time = Column(
        DateTime, nullable=False
    )
    on_schedule = Column(
        BIT(1), nullable=False
    )
    ticket_price = Column(
        Float(),
        nullable=False,
    )
    __table_args__ = (
        UniqueConstraint(
            "show_time", "hall_id", "film_id",
            name='_schedule_details'
        ),
    )


class BookingsRecord(Base):
    __tablename__ = "booking"
    id = Column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
    )
    seat_no = Column(
        String(50, collation=_COLLATION),
        nullable=False,
    )
    schedule_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("schedule.schedule_id"),
        nullable=False,
    )
    status = Column(
        Enum("ACTIVE", "CANCELLED", collation=_COLLATION),
        nullable=False, default="ACTIVE"
    )
    account_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("account.id"),
        nullable=True,
    )
    amount = Column(
        Float(),
        nullable=False,
    )
    person_type_id = Column(
        INTEGER(unsigned=True),
        ForeignKey("person_type.person_type_id"),
        nullable=False,
    )
    serial_no = Column(
        String(6, collation=_COLLATION),
        nullable=False, unique=True, default=text("generate_unique_string()")
    )
    batch_ref = Column(
        String(50, collation=_COLLATION),
        nullable=False,
    )
    created = Column(
        DateTime(), default=func.now(), nullable=False
    )
    assigned_user = Column(
        String(50, collation=_COLLATION), ForeignKey("user.email"),
        nullable=False,
    )
    __table_args__ = (
        UniqueConstraint(
            "seat_no", "schedule_id",
            name='_schedule_details'
        ),
    )
