from typing import List

from pydantic import BaseModel


class Test:

    def __init__(
            self, req_url_path: str, res_status_code: int,
            req_type: str,
            req_params: dict | None = None,
            req_body: BaseModel | None | List[BaseModel] = None,
            test_id: int | None = None,
            ):
        self.test_id = test_id
        self.req_url_path = req_url_path
        self.res_status_code = res_status_code
        self.req_type = req_type
        self.req_params = req_params
        self.req_body = req_body
