from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Union

import requests
from pyexpat import ExpatError
from requests import HTTPError, Response
from requests.structures import CaseInsensitiveDict

from ..models.basemodel import APIBaseModel
from ..models.exceptions import ExceptionList, ResponseError
from .content_type import SUPPORTED_REQUEST_CONTENT_TYPES, content_types_match


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
        from ..api import API
        if isinstance(obj, API):
            self._stack = [obj]
        else:
            self._stack = obj._stack.copy()
            self._stack.append(obj)
        return self

    def _build_url(self) -> str:
        """
        Builds and returns the URL using all the stack information.
        The first item in the stack must be an `API` instance, and the rest
        must be `APIResource` instances.
        """
        from ..api import API
        if len(self._stack) == 0 or not isinstance(self._stack[0], API):
            raise Exception("API instance is missing in the stack")

        return self._stack[0].host.rstrip("/") + self._build_path()

    def _build_path(self) -> str:
        """
        Builds the URL path using all the `APIResource` instances in the stack.
        """
        path = ""
        for obj in self._stack:
            if isinstance(obj, APIResource):
                path = path + obj._build_partial_path()

        return path + self._build_partial_path()

    def _make_request(self, method="GET", body=None, req_content_types: list = None, **kwargs) -> Response:
        from ..api import API
        if len(self._stack) == 0 or not isinstance(self._stack[0], API):
            raise Exception("API instance is missing in the stack")

        body, headers = _validate_request_payload(body, req_content_types, kwargs.get('headers'))
        kwargs['headers'] = headers

        api = self._stack[0]
        return api.make_request(method, self._build_path(), body=body, **kwargs)

    def _handle_response(self, response: requests.Response, expected_responses: list):
        expected_status_codes = set([r[0] for r in expected_responses])
        if response.status_code not in expected_status_codes:
            raise Exception(f"Unexpected response status code ({response.status_code})")

        resp_content_type = response.headers.get('content-type')
        for r in expected_responses:
            code, content_type, resp_class = r

            if not content_type:
                ret = resp_class()
                ret._http_response = response
                return self._handle_error(ret)

            if response.status_code == code and resp_content_type.startswith(content_type):
                resp_payload = response.content
                if resp_content_type.startswith('application/json'):
                    resp_payload = response.json()
                elif resp_content_type.startswith('application/xml'):
                    import xmltodict
                    resp_payload = xmltodict.parse(response.content)['root']

                ret = resp_class.parse_obj(resp_payload)
                ret._http_response = response
                return self._handle_error(ret)

        raise Exception(f"Unexpected response content type ({resp_content_type})")

    def _handle_error(self, ret):
        api = self._stack[0]
        if api._raise_errors:
            try:
                ret.http_response().raise_for_status()
            except HTTPError as e:
                raise ResponseError(ret, str(e))

        return ret


def _validate_request_payload(body: Union[str, bytes, dict, APIBaseModel],
                              req_content_types: list, headers: dict) -> tuple[str, dict]:
    """
    Tries to parse the request body into one of the supported pairs of
    content-type / class type. An exception will be returned if the body
    doesn't match any of the given expected types.

    If req_content_types is None or an empty list, this is a no-op.

    :param body:              Payload of the request.
    :param req_content_types: List of tuples defining the supported types of the
                              request. The first element of each tuple is the
                              Content-Type, and the second one is the class of
                              the payload model.
    :param headers:           The headers of the request. If a Content-Type is
                              set, only the types in req_content_types that
                              matches that Content-Type will be validated.
    :return:                  The body ready to be sent, and the headers with
                              the proper Content-Type added.
    """
    exceptions_raised = []

    if req_content_types:
        content_type_defined = False

        # If Content-Type header is set, only that one is allowed
        headers = CaseInsensitiveDict(headers)
        headers.items()
        expected_content_type = headers.get('content-type', None)
        if expected_content_type:
            content_type_defined = True
            req_content_types = [(content_type, req_class) for content_type, req_class in req_content_types if
                                 content_types_match(content_type, expected_content_type)]

        for content_type, request_class in req_content_types:
            # TODO: currently, request_class is not used, but it could be used
            #       to validate that the payload matches a given model
            for ct, conv_func in SUPPORTED_REQUEST_CONTENT_TYPES.items():
                if content_types_match(content_type, ct):
                    try:
                        body = conv_func(body)

                        if not content_type_defined:
                            # Set content type header
                            headers['Content-Type'] = content_type
                        return body, dict(headers)
                    except (ValueError, ExpatError) as e:
                        exceptions_raised.append(e)

    if len(exceptions_raised) > 0:
        raise ExceptionList('nooo', exceptions_raised)

    return body, headers
