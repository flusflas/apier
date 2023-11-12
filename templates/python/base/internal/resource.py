from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import requests
from requests import Response


@dataclass
class APIResource(ABC):
    """
    Abstract class to represent a part of an API call.
    This must be inherited by any class implementing an API operation.
    """

    _stack: list = field(default_factory=list, init=False)
    """
    A list used to store the objects generated during a call chain.
    This allows to access all the information needed to make an API request,
    such as building the request URL.

    Items in the stack can be:
    - One (and only one) `API` instance. This must be the first item in the
      stack.
    - A number of `APIResource` building the request.
    """

    @abstractmethod
    def _build_partial_path(self):
        pass

    def _with_stack(self, stack: list):
        self._stack = stack
        return self

    def _child_of(self, obj):
        """
        Sets the stack of this instance to a copy of the given `APIResource`
        stack with the object itself added.
        This method is used when a new `APIResource` instance is created from
        another one.
        """
        from _build.api import API
        if isinstance(obj, API):
            self._stack = [obj]
        else:
            self._stack = obj._stack.copy()
            self._stack.append(obj)
        return self

    def build_url(self) -> str:
        """
        Builds and returns the URL using all the stack information.
        The first item in the stack must be an `API` instance, and the rest
        must be `APIResource` instances.
        """
        from _build.api import API
        if len(self._stack) == 0 or not isinstance(self._stack[0], API):
            raise Exception("API instance is missing in the stack")

        return self._stack[0].host.rstrip("/") + self.build_path()

    def build_path(self) -> str:
        """
        Builds the URL path using all the `APIResource` instances in the stack.
        """
        path = ""
        for obj in self._stack:
            if isinstance(obj, APIResource):
                path = path + obj._build_partial_path()

        return path + self._build_partial_path()

    def _make_request(self, method="GET", body=None, **kwargs) -> Response:
        from _build.api import API
        if len(self._stack) == 0 or not isinstance(self._stack[0], API):
            raise Exception("API instance is missing in the stack")

        api = self._stack[0]
        return api.make_request(method, self.build_path(), body=body, **kwargs)


def handle_response(response: requests.Response, expected_responses: list):
    expected_status_codes = set([r[0] for r in expected_responses])
    if response.status_code not in expected_status_codes:
        raise Exception(f"Unexpected response status code ({response.status_code})")

    resp_content_type = response.headers.get('content-type')
    for r in expected_responses:
        code, content_type, resp_class = r

        if not content_type:
            ret = resp_class()
            ret._http_response = response
            return ret

        if response.status_code == code and resp_content_type.startswith(content_type):
            resp_payload = response.content
            if resp_content_type.startswith('application/json'):
                resp_payload = response.json()
            elif resp_content_type.startswith('application/xml'):
                import xmltodict
                resp_payload = xmltodict.parse(response.content)['root']

            ret = resp_class.parse_obj(resp_payload)
            ret._http_response = response
            return ret

    raise Exception(f"Unexpected response content type ({resp_content_type})")
