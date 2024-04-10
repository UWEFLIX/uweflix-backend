from src.schema.bookings import PersonType


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
