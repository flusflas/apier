import json
import math

from httpretty.core import HTTPrettyRequest

from tests.templates.setup import build_client
from .common import assert_pagination

build_client("python-tree", "pagination_api.yaml")
if True:
    from ._build.api import API
    from ._build.models.models import Result

expected_results = [
    {"value": 0},
    {"value": 1},
    {"value": 2},
    {"value": 3},
    {"value": 4},
    {"value": 5},
    {"value": 6},
    {"value": 7},
    {"value": 8},
    {"value": 9},
]


def test_cursor_pagination():
    """
    Tests a successful pagination using Cursor pagination.
    """
    pagination_function = API().pagination().cursor().get

    for limit in range(1, 10):

        def request_handler(req: HTTPrettyRequest, uri, response_headers):
            assert "foo" in req.querystring
            assert "limit" in req.querystring
            assert int(req.querystring["limit"][0]) == limit

            data = []
            next_cursor, prev_cursor = None, None
            next_index, prev_index = len(expected_results), -1

            next_cursor_param = req.querystring.get("next", None)
            if next_cursor_param:
                next_cursor_param = int(next_cursor_param[0])
                for i, item in enumerate(expected_results):
                    if item["value"] >= next_cursor_param:
                        data = expected_results[i : i + limit]
                        next_index = i + limit
                        prev_index = i - 1
                        break
            else:
                data = expected_results[:limit]
                next_index = limit
                prev_index = -1

            if next_index < len(expected_results):
                next_cursor = str(expected_results[next_index]["value"])
            if prev_index >= 0:
                prev_cursor = str(expected_results[prev_index]["value"])

            resp = {
                "results": data,
                "cursors": {"next": next_cursor, "prev": prev_cursor},
            }

            response_headers["Content-Type"] = "application/json"
            return [200, response_headers, json.dumps(resp)]

        assert_pagination(
            pagination_function=pagination_function,
            function_params={"params": {"limit": str(limit), "foo": "bar"}},
            request_handler=request_handler,
            get_response_data=lambda response: response.results,
            expected_url="https://pagination.test/pagination/cursor",
            expected_results=expected_results,
            expected_limit=limit,
            expected_call_count=math.ceil(len(expected_results) / limit),
            expected_type=Result,
        )


def test_next_page_url_pagination():
    """
    Tests a successful pagination using Next Page URL pagination.
    """
    pagination_function = API().pagination().next_page_url().get

    for limit in range(1, 10):

        def request_handler(req: HTTPrettyRequest, uri, response_headers):
            # assert 'foo' in req.querystring
            assert "limit" in req.querystring
            assert int(req.querystring["limit"][0]) == limit

            data = []
            next_page_url = ""
            next_index, _ = len(expected_results), -1

            next_cursor_param = req.querystring.get("next_page_url", None)
            if next_cursor_param:
                next_cursor_param = int(next_cursor_param[0])
                for i, item in enumerate(expected_results):
                    if item["value"] >= next_cursor_param:
                        data = expected_results[i : i + limit]
                        next_index = i + limit
                        break
            else:
                data = expected_results[:limit]
                next_index = limit

            if next_index < len(expected_results):
                next_cursor = str(expected_results[next_index]["value"])
                next_page_url = (
                    f"https://pagination.test/pagination/next_page_url"
                    f"?next_page_url={next_cursor}&limit={limit}"
                )

            resp = {"results": data, "next_page_url": next_page_url}

            response_headers["Content-Type"] = "application/json"
            return [200, response_headers, json.dumps(resp)]

        assert_pagination(
            pagination_function=pagination_function,
            function_params={"params": {"limit": str(limit), "foo": "bar"}},
            request_handler=request_handler,
            get_response_data=lambda response: response.results,
            expected_url="https://pagination.test/pagination/next_page_url",
            expected_results=expected_results,
            expected_limit=limit,
            expected_call_count=math.ceil(len(expected_results) / limit),
            expected_type=Result,
        )


def test_offset_pagination():
    """
    Tests a successful pagination using offset pagination.
    """
    pagination_function = API().pagination().offset().get

    for limit in range(1, 10):

        def request_handler(req: HTTPrettyRequest, uri, response_headers):
            assert "foo" in req.querystring
            assert "limit" in req.querystring
            assert int(req.querystring["limit"][0]) == limit

            offset = int(req.querystring.get("offset", [0])[0])

            next_index_start = offset
            next_index_end = offset + limit

            if next_index_end > len(expected_results):
                next_index_end = len(expected_results)

            if next_index_start >= len(expected_results):
                data = []
            else:
                data = expected_results[next_index_start:next_index_end]

            resp = {"results": data}

            response_headers["Content-Type"] = "application/json"
            return [200, response_headers, json.dumps(resp)]

        expected_call_count = math.ceil(len(expected_results) / limit)
        if len(expected_results) % limit == 0:
            expected_call_count += 1

        assert_pagination(
            pagination_function=pagination_function,
            function_params={"params": {"limit": str(limit), "foo": "bar"}},
            request_handler=request_handler,
            get_response_data=lambda response: response.results,
            expected_url="https://pagination.test/pagination/offset",
            expected_results=expected_results,
            expected_limit=limit,
            expected_call_count=expected_call_count,
            expected_type=Result,
        )


def test_page_pagination():
    """
    Tests a successful pagination using page pagination.
    """
    pagination_function = API().pagination().page().get

    for page_size in range(1, 10):

        def request_handler(req: HTTPrettyRequest, uri, response_headers):
            assert "foo" in req.querystring
            assert "page_size" in req.querystring
            assert int(req.querystring["page_size"][0]) == page_size

            page = int(req.querystring.get("page", [0])[0])

            next_index_start = page * page_size
            next_index_end = next_index_start + page_size

            if next_index_end > len(expected_results):
                next_index_end = len(expected_results)

            if next_index_start >= len(expected_results):
                data = []
            else:
                data = expected_results[next_index_start:next_index_end]

            resp = {"results": data}

            response_headers["Content-Type"] = "application/json"
            return [200, response_headers, json.dumps(resp)]

        expected_call_count = math.ceil(len(expected_results) / page_size)
        if len(expected_results) % page_size == 0:
            expected_call_count += 1

        assert_pagination(
            pagination_function=pagination_function,
            function_params={"params": {"page_size": str(page_size), "foo": "bar"}},
            request_handler=request_handler,
            get_response_data=lambda response: response.results,
            expected_url="https://pagination.test/pagination/page",
            expected_results=expected_results,
            expected_limit=page_size,
            expected_call_count=expected_call_count,
            expected_type=Result,
        )
