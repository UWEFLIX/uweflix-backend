from src.schema.bookings import PersonType, Booking
from src.schema.factories.account_factory import AccountsFactory
from src.schema.factories.film_factories import FilmFactory


class BookingsFactory:
    @staticmethod
    def get_person_type(record):
        return PersonType(
            id=record.person_type_id,
            person_type=record.person_type,
            discount_amount=record.discount_amount,
        )

    @staticmethod
    def get_person_types(records):
        return [
            BookingsFactory.get_person_type(x) for x in records
        ]

    @staticmethod
    def get_booking(records):
        booking_record = records[0]

        if records[4]:
            account = AccountsFactory.get_half_account(records[4])
        else:
            account = None

        return Booking(
            id=booking_record.id,
            seat_no=booking_record.seat_no,
            created=booking_record.created,
            assigned_user=booking_record.assigned_user,
            schedule=FilmFactory.get_detailed_schedule([
                records[1], records[2], records[3]
            ]),
            status=booking_record.status,
            account=account,
            person_type=BookingsFactory.get_person_type(records[5]),
            amount=booking_record.amount,
            serial_no=booking_record.serial_no,
            batch_ref=booking_record.batch_ref,
        )

    @staticmethod
    def get_bookings(records):
        return [
            BookingsFactory.get_booking(x) for x in records
        ]

    @staticmethod
    def get_half_bookings(records):
        return [
            {
                "id": record.id,
                "seat_no": record.seat_no,
                "schedule": record.schedule_id,
                "status": record.status,
                "account": record.account_id,
                "person_type": record.person_type_id,
                "amount": record.amount,
                "serial_no": record.serial_no,
                "batch_ref": record.batch_ref,
                "created": record.created,
                "assigned_user": record.assigned_user
            } for record in records
        ]
