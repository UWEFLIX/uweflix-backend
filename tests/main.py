from src.utils.db_initialzation import main as db_init
from tests._test import Test
from tests.client import Client


def main():
    db_init()

    client = Client()
    client.login()

    reqs = {
        "1": Test(
            test_id=1,
            req_url_path="/clubs/cities/city",
            res_status_code=201,
            req_type="post",
            req_params={"city_name": "Addu"},
            req_body=None,
        ),
        "2": Test(
            test_id=2,
            req_url_path="/clubs/cities/city",
            res_status_code=201,
            req_type="post",
            req_params={"city_name": "Addu"},
            req_body=None,
        )
    }

    for i_id, item in reqs.items():
        client.req(item)


