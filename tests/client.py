import os
import json
import requests

from tests._logger import get_logger
from tests._test import Test


class Client:
    def __init__(self):
        self._headers: dict | None = None
        host = os.getenv("HOST")
        port = os.getenv("PORT")

        self._pass = os.getenv("ADMIN1_PASSWORD")
        self._user = os.getenv("ADMIN1_EMAIL")

        if host == "0.0.0.0":
            _host = "127.0.0.1"
        else:
            _host = host
        _ssl = int(os.getenv("SSL"))

        if _ssl:
            schema = "https"
            self._verify = True
        else:
            schema = "http"
            self._verify = False

        self._server = f"{schema}://{_host}:{port}"
        self._logger = get_logger(f"Logging {__name__}")

    def login(self):
        data = (
            f'grant_type=&username={self._user}'
            f'&password={self._pass}&scope=&client_id=&client_secret=')
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(
            f"{self._server}/token",
            data=data,
            headers=headers,
            verify=self._verify
        )
        content = json.loads(response.content)

        _token = content["access_token"]
        token_type = content["token_type"]
        token = f"{token_type} {_token}"

        self._headers = {
            'accept': 'application/json',
            "Authorization": token
        }

    def req(self, _test: Test):
        if _test.req_body is not None:

            if type(_test.req_body) is list:
                _body = [
                    x.model_dump() for x in _test.req_body
                ]
            else:
                _body = _test.req_body.model_dump()
        else:
            _body = None

        if _test.req_type == "post":
            response = requests.post(
                url=f"{self._server}{_test.req_url_path}",
                json=_body, params=_test.req_params,
                headers=self._headers,
                verify=self._verify
            )
        elif _test.req_type == "patch":
            response = requests.patch(
                url=f"{self._server}{_test.req_url_path}",
                json=_body, params=_test.req_params,
                headers=self._headers,
                verify=self._verify
            )
        else:
            raise Exception("invalid req type")

        if response.status_code != _test.res_status_code:
            self._logger.error(
                f"Test ID: {_test.test_id} returned {response.status_code} "
                f"expected: {_test.res_status_code}"
            )
            self._logger.error(f"Request body: {_test.req_body}")

            if response.status_code >= 500 or response.status_code == 204:
                return

            self._logger.error(
                f"Response: {json.loads(response.content.decode())}"
            )
        else:
            self._logger.info(
                f"Test ID: {_test.test_id} succeeded"
            )
