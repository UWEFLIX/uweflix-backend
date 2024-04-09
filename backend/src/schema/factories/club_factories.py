from typing import List

from src.schema.clubs import City


class ClubFactory:
    @staticmethod
    def get_city(record) -> City:
        return City(
            id=record.city_id,
            name=record.city_name
        )

    @staticmethod
    def get_cities(records: list) -> List[City]:
        return [
            ClubFactory.get_city(x) for x in records
        ]
