class Test:

    def __init__(
            self, test_id: int, req_url_path: str, res_status_code: int,
            req_type: str,
            req_params: dict | None = None,
            req_body: dict | None = None,
            ):
        self.test_id = test_id,
        self.req_url_path = req_url_path
        self.res_status_code = res_status_code
        self.req_type = req_type
        self.req_params = req_params
        self.req_body = req_body
