from src.schema.bookings import PersonType
from src.schema.films import Hall, Film
from src.utils.db_initialzation import main as db_init
from tests._test import Test
from tests.client import Client


def main():
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
            req_body=None,
            req_params={"role_name": "Account Manager"}
        ),
        "20": Test(
            req_url_path="/users/roles/role",
            res_status_code=201,
            req_type="post",
            req_body=None,
            req_params={"role_name": "Clerk"}
        ),
        "21": Test(
            req_url_path="/users/roles/role",
            res_status_code=201,
            req_type="post",
            req_body=None,
            req_params={"role_name": "Cinema Manager"}
        ),
        "22": Test(
            req_url_path="/users/roles/role",
            res_status_code=201,
            req_type="post",
            req_body=None,
            req_params={"role_name": "Receptionist"}
        ),
        "23": Test(
            req_url_path="/users/roles/role",
            res_status_code=201,
            req_type="post",
            req_body=None,
            req_params={"role_name": "Sales Manager"}
        ),
        "24": Test(
            req_url_path="/users/roles/role",
            res_status_code=201,
            req_type="post",
            req_body=None,
            req_params={"role_name": "Sales Representative"}
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

    user_reqs = {
        "27": Test(
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
    }

    reqs.update(user_reqs)

    for i_id, item in reqs.items():
        item.test_id = i_id
        client.req(item)


