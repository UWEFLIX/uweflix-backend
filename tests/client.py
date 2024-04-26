import os
import json
import requests

from tests._test import Test


class Client:
    def __init__(self):
        pass

        self._headers = None
        host = os.getenv("host")
        port = os.getenv("port")

        self._server = f"http://{host}:{port}"

    def login(self):
        username = "nishawl.naseer@outlook.com"
        password = "123"
        data = f'grant_type=&username={username}&password={password}&scope=&client_id=&client_secret='
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(
            f"{self._server}/token",
            data=data,
            headers=headers,
            verify=False
        )
        print(response.status_code)
        content = json.loads(response.content)
        print(content)

        _token = content["access_token"]
        token_type = content["token_type"]
        token = f"{token_type} {_token}"

        self._headers = {
            'accept': 'application/json',
            "Authorization": token
        }

    def req(self, _test: Test):
        if _test.req_type == "post":
            response = requests.post(
                url=f"{self._server}{_test.req_url_path}",
                json=_test.req_body, params=_test.req_params, headers=self._headers, verify=False
            )
        elif _test.req_type == "patch":
            response = requests.patch(
                url=f"{self._server}{_test.req_url_path}",
                json=_test.req_body, params=_test.req_params, headers=self._headers, verify=False
            )
        else:
            raise Exception("invalid req type")

        if response.status_code != _test.res_status_code:
            print(f"{_test.test_id} returned {response.status_code}")
