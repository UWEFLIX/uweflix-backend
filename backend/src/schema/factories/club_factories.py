from typing import List

from src.schema.clubs import City, Club
from src.schema.factories.user_factory import UserFactory


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

    @staticmethod
    def get_full_club(mp: dict) -> Club:
        club_record = mp["club"]
        city_record = mp["city"]
        leader_record = mp["leader"]
        member_records = mp["members"]

        club = ClubFactory.get_half_club([club_record, city_record])
        club.leader = UserFactory.create_half_user(leader_record)
        club.members = UserFactory.create_half_users(member_records)

        return club

    @staticmethod
    def get_half_club(record) -> Club:
        city_record = record[1]
        club_record = record[0]
        return Club(
            id=club_record.id,
            club_name=club_record.club_name,
            addr_street_number=club_record.addr_street_number,
            addr_street_name=club_record.addr_street_name,
            email=club_record.email,
            contact_number=club_record.contact_number,
            landline_number=club_record.landline_number,
            post_code=club_record.post_code,
            city=ClubFactory.get_city(city_record),
            status=club_record.status
        )

    @staticmethod
    def get_half_clubs(records) -> List[Club]:
        return [
            ClubFactory.get_half_club(x) for x in records
        ]
