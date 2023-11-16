from requests import Response


class APIException(Exception):
    pass


class ResponseError(APIException):
    """ Client or server error response. """

    def __init__(self, error, *attr):
        super().__init__(*attr)
        self.error = error

    def http_response(self) -> Response:
        return self.error.http_response()
