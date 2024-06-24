import random
from datetime import datetime
from typing import Dict

from icecream import ic

from src.schema.bookings import PersonType
from src.schema.clubs import Club, City
from src.schema.films import Hall, Film, Schedule
from src.schema.users import User, Role
from src.utils.db_initialzation import main as db_init
from tests._test import Test
from tests.client import Client
from faker import Faker


def main(USER_COUNT: int, NO_CLUBS: int):
    db_init()

    client = Client()
    client.login()

    reqs = {
        "1": Test(
            req_url_path="/clubs/cities/city",
            res_status_code=201,
            req_type="post",
            req_params={"city_name": "London"},
            req_body=None,
        ),
        "2": Test(
            req_url_path="/clubs/cities/city",
            res_status_code=201,
            req_type="post",
            req_params={"city_name": "Manchester"},
            req_body=None,
        ),
        "3": Test(
            req_url_path="/clubs/cities/city",
            res_status_code=201,
            req_type="post",
            req_params={"city_name": "Liverpool"},
            req_body=None,
        ),
        "4": Test(
            req_url_path="/clubs/cities/city",
            res_status_code=201,
            req_type="post",
            req_params={"city_name": "Glasgow"},
            req_body=None,
        ),
        "5": Test(
            req_url_path="/clubs/cities/city",
            res_status_code=201,
            req_type="post",
            req_params={"city_name": "Southampton"},
            req_body=None,
        ),
        "6": Test(
            req_url_path="/films/halls/hall",
            res_status_code=201,
            req_type="post",
            req_body=Hall(
                id=0,
                hall_name="Qasim Ibrahim Hall",
                seats_per_row=12,
                no_of_rows=12,
            ),
        ),
        "7": Test(
            req_url_path="/films/halls/hall",
            res_status_code=201,
            req_type="post",
            req_body=Hall(
                id=0,
                hall_name="Ahmed Anwar Hall",
                seats_per_row=11,
                no_of_rows=11,
            ),
        ),
        "8": Test(
            req_url_path="/films/halls/hall",
            res_status_code=201,
            req_type="post",
            req_body=Hall(
                id=0,
                hall_name="East Wing Hall",
                seats_per_row=13,
                no_of_rows=13,
            ),
        ),
        "9": Test(
            req_url_path="/films/halls/hall",
            res_status_code=201,
            req_type="post",
            req_body=Hall(
                id=0,
                hall_name="West Wing Hall",
                seats_per_row=13,
                no_of_rows=13,
            ),
        ),
        "10": Test(
            req_url_path="/films/halls/hall",
            res_status_code=201,
            req_type="post",
            req_body=Hall(
                id=0,
                hall_name="North Wing Hall",
                seats_per_row=13,
                no_of_rows=13,
            ),
        ),
        "11": Test(
            req_url_path="/films/halls/hall",
            res_status_code=201,
            req_type="post",
            req_body=Hall(
                id=0,
                hall_name="South Wing Hall",
                seats_per_row=13,
                no_of_rows=13,
            ),
        ),
        "12": Test(
            req_url_path="/films/film",
            res_status_code=201,
            req_type="post",
            req_body=Film(
                id=0,
                title="Inception",
                age_rating="Child",
                duration_sec=120,
                trailer_desc="Who doesnt know Inception",
                on_air_from="2024-01-01T00:00:00.00Z",
                on_air_to="2025-01-01T00:00:00.00Z",
                is_active=True,
            ),
        ),
        "13": Test(
            req_url_path="/films/film",
            res_status_code=201,
            req_type="post",
            req_body=Film(
                id=0,
                title="Interstellar",
                age_rating="Child",
                duration_sec=120,
                trailer_desc="Who doesnt know Interstellar",
                on_air_from="2024-01-01T00:00:00.00Z",
                on_air_to="2025-01-01T00:00:00.00Z",
                is_active=False,
            ),
        ),
        "14": Test(
            req_url_path="/films/film",
            res_status_code=201,
            req_type="post",
            req_body=Film(
                id=0,
                title="Shawshank Redemption",
                age_rating="Child",
                duration_sec=120,
                trailer_desc="Who doesnt know Shawshank Redemption",
                on_air_from="2024-01-01T00:00:00.00Z",
                on_air_to="2025-04-01T00:00:00.00Z",
                is_active=False,
            ),
        ),
        "15": Test(
            req_url_path="/films/film",
            res_status_code=201,
            req_type="post",
            req_body=Film(
                id=0,
                title="Insidious Chapter 3",
                age_rating="Child",
                duration_sec=120,
                trailer_desc="Who doesnt know Insidious Chapter 3",
                on_air_from="2024-01-01T00:00:00.00Z",
                on_air_to="2025-04-01T00:00:00.00Z",
                is_active=False,
            ),
        ),
        "16": Test(
            req_url_path="/films/film",
            res_status_code=201,
            req_type="post",
            req_body=Film(
                id=0,
                title="Insidious Chapter 4",
                age_rating="Adult",
                duration_sec=120,
                trailer_desc="Who doesnt know Insidious Chapter 4",
                on_air_from="2024-01-01T00:00:00.00Z",
                on_air_to="2025-06-01T00:00:00.00Z",
                is_active=False,
            ),
        ),
        "17": Test(
            req_url_path="/films/film",
            res_status_code=201,
            req_type="post",
            req_body=Film(
                id=0,
                title="Insidious Chapter 5",
                age_rating="Child",
                duration_sec=120,
                trailer_desc="Who doesnt know Insidious Chapter 5",
                on_air_from="2024-01-01T00:00:00.00Z",
                on_air_to="2025-06-01T00:00:00.00Z",
                is_active=False,
            ),
        ),
        "18": Test(
            req_url_path="/films/film",
            res_status_code=201,
            req_type="post",
            req_body=Film(
                id=0,
                title="Insidious Chapter 6",
                age_rating="Child",
                duration_sec=120,
                trailer_desc="Who doesnt know Insidious Chapter 6",
                on_air_from="2024-01-01T00:00:00.00Z",
                on_air_to="2025-06-01T00:00:00.00Z",
                is_active=False,
            ),
        ),
        "19": Test(
            req_url_path="/users/roles/role",
            res_status_code=201,
            req_type="post",
            req_body=Role(
                id=0,
                name="Account Manager",
                permissions=[]
            ),
        ),
        "20": Test(
            req_url_path="/users/roles/role",
            res_status_code=201,
            req_type="post",
            req_body=Role(
                id=0,
                name="Clerk",
                permissions=[]
            ),
        ),
        "21": Test(
            req_url_path="/users/roles/role",
            res_status_code=201,
            req_type="post",
            req_body=Role(
                id=0,
                name="Cinema Manager",
                permissions=[]
            ),
        ),
        "22": Test(
            req_url_path="/users/roles/role",
            res_status_code=201,
            req_type="post",
            req_body=Role(
                id=0,
                name="Receptionist",
                permissions=[]
            ),
        ),
        "23": Test(
            req_url_path="/users/roles/role",
            res_status_code=201,
            req_type="post",
            req_body=Role(
                id=0,
                name="Sales Manager",
                permissions=[]
            ),
        ),
        "24": Test(
            req_url_path="/users/roles/role",
            res_status_code=201,
            req_type="post",
            req_body=Role(
                id=0,
                name="Sales Representative",
                permissions=[]
            ),
        ),
        "25": Test(
            req_url_path="/bookings/person-types/person-type",
            res_status_code=201,
            req_type="post",
            req_body=PersonType(
                id=0, person_type="Child", discount_amount=20,
            ),
            # req_params={"role_name": "Sales Manager"}
        ),
        "26": Test(
            req_url_path="/bookings/person-types/person-type",
            res_status_code=201,
            req_type="post",
            req_body=PersonType(
                id=0, person_type="Student", discount_amount=10,
            ),
            # req_params={"role_name": "Sales Manager"}
        )
    }

    count = len(reqs)+1

    for x in range(USER_COUNT):
        fake = Faker("en_GB")
        _test = Test(
            req_url_path="/users/user",
            res_status_code=201,
            req_type="post",
            req_body=User(
                id=1,
                name=fake.name(),
                email=fake.email(),
                status="ENABLED",
            )
        )
        reqs.update({str(count): _test})

        count += 1
    
    members = {}
    free_users = [x for x in range(1, USER_COUNT+1)]
    random.shuffle(free_users)
    clubs_num = int(USER_COUNT / 10)
    for x in range(clubs_num):
        fake = Faker("en_GB")
        leader = free_users.pop()
            
        members[leader] = True

        _test = Test(
            req_url_path="/clubs/club",
            res_status_code=201,
            req_type="post",
            req_body=Club(
                id=1,
                leader=User(
                    id=leader,
                    name=fake.name(),
                    email=fake.email(),
                    status="ENABLED",
                ),
                club_name=fake.company(),
                addr_street_number=str(random.randint(1, 200)),
                addr_street_name=fake.street_name(),
                email=fake.email(),
                contact_number=fake.phone_number(),
                landline_number=str(fake.random_number()),
                post_code=random.randint(1, 20000),
                city=City(
                    id=random.randint(1, 5),
                    name="Name"
                ),
                status="ENABLED",
            )
        )

        reqs.update({str(count): _test})
        count += 1

    for i_id, item in reqs.items():
        try:
            item.test_id = i_id
        except AttributeError:
            pass
        client.req(item)

    ic(f"Count before schedules: {count}")

    schedules = {
        count+1: Test(
            req_url_path="/films/schedules/schedule",
            res_status_code=201,
            req_type="post",
            req_body=Schedule(
                id=1,
                hall_id=1,
                film_id=1,
                show_time=datetime(
                    year=2024, day=22, month=11, hour=13,
                    minute=00
                ),
                on_schedule=1,
                ticket_price=7,
                class_name="0",
            ),
        ),
        count + 2: Test(
            req_url_path="/films/schedules/schedule",
            res_status_code=201,
            req_type="post",
            req_body=Schedule(
                id=1,
                hall_id=1,
                film_id=1,
                show_time=datetime(
                    year=2024, day=22, month=11, hour=17,
                    minute=00
                ),
                on_schedule=1,
                ticket_price=7,
                class_name="0",
            ),
        ),
        count + 3: Test(
            req_url_path="/films/schedules/schedule",
            res_status_code=201,
            req_type="post",
            req_body=Schedule(
                id=1,
                hall_id=1,
                film_id=1,
                show_time=datetime(
                    year=2024, day=22, month=11, hour=21,
                    minute=00
                ),
                on_schedule=1,
                ticket_price=7,
                class_name="0",
            ),
        ),
        count + 4: Test(
            req_url_path="/films/schedules/schedule",
            res_status_code=201,
            req_type="post",
            req_body=Schedule(
                id=1,
                hall_id=1,
                film_id=1,
                show_time=datetime(
                    year=2024, day=23, month=11, hour=17,
                    minute=00
                ),
                on_schedule=1,
                ticket_price=7,
                class_name="0",
            ),
        ),
        count + 5: Test(
            req_url_path="/films/schedules/schedule",
            res_status_code=201,
            req_type="post",
            req_body=Schedule(
                id=1,
                hall_id=1,
                film_id=1,
                show_time=datetime(
                    year=2024, day=23, month=11, hour=21,
                    minute=00
                ),
                on_schedule=1,
                ticket_price=7,
                class_name="0",
            ),
        )
    }

    count += len(schedules)

    for i_id, item in schedules.items():
        try:
            item.test_id = i_id
        except AttributeError:
            pass
        client.req(item)
