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
        records.pop(0)

        return Booking(
            id=booking_record.id,
            seat_no=booking_record.seat_no,
            entity_type=booking_record.entity_type,
            entity_id=booking_record.entity_id,
            schedule=FilmFactory.get_detailed_schedule(records),
            status=booking_record.status,
            account=AccountsFactory.get_half_account(records[4]),
            person_type=BookingsFactory.get_person_type(records[5]),
            amount=booking_record.amount,
            serial_no=booking_record.serial_no,
            batch_ref=booking_record.batch_ref,
        )
