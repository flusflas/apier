import json

from httpretty.core import HTTPrettyRequest

from _build.api import API
from _build.models.models import Result
from .common import assert_pagination

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

    for limit in range(4, 5):
        def request_handler(req: HTTPrettyRequest, uri, response_headers):
            assert 'foo' in req.querystring
            assert 'limit' in req.querystring
            assert int(req.querystring['limit'][0]) == limit

            data = []
            next_cursor, prev_cursor = None, None
            next_index, prev_index = len(expected_results), -1

            next_cursor_param = req.querystring.get('next', None)
            if next_cursor_param:
                next_cursor_param = int(next_cursor_param[0])
                for i, item in enumerate(expected_results):
                    if item['value'] >= next_cursor_param:
                        data = expected_results[i:i + limit]
                        next_index = i + limit
                        prev_index = i - 1
                        break
            else:
                data = expected_results[:limit]
                next_index = limit
                prev_index = -1

            if next_index < len(expected_results):
                next_cursor = str(expected_results[next_index]['value'])
            if prev_index >= 0:
                prev_cursor = str(expected_results[prev_index]['value'])

            resp = {
                "results": data,
                "cursors": {
                    "next": next_cursor,
                    "prev": prev_cursor
                }
            }

            response_headers['Content-Type'] = 'application/json'
            return [200, response_headers, json.dumps(resp)]

        assert_pagination(pagination_function,
                          {'params': {'limit': str(limit), 'foo': 'bar'}},
                          request_handler,
                          lambda response: response.results,
                          "https://pagination.test/pagination/cursor",
                          expected_results, limit, Result)


def test_next_page_url_pagination():
    """
    Tests a successful pagination using Next Page URL pagination.
    """
    pagination_function = API().pagination().next_page_url().get

    for limit in range(4, 5):
        def request_handler(req: HTTPrettyRequest, uri, response_headers):
            # assert 'foo' in req.querystring
            assert 'limit' in req.querystring
            assert int(req.querystring['limit'][0]) == limit

            data = []
            next_page_url = ''
            next_index, prev_index = len(expected_results), -1

            next_cursor_param = req.querystring.get('next_page_url', None)
            if next_cursor_param:
                next_cursor_param = int(next_cursor_param[0])
                for i, item in enumerate(expected_results):
                    if item['value'] >= next_cursor_param:
                        data = expected_results[i:i + limit]
                        next_index = i + limit
                        break
            else:
                data = expected_results[:limit]
                next_index = limit

            if next_index < len(expected_results):
                next_cursor = str(expected_results[next_index]['value'])
                next_page_url = f"https://pagination.test/pagination/next_page_url?next_page_url={next_cursor}&limit={limit}"

            resp = {
                "results": data,
                "next_page_url": next_page_url
            }

            response_headers['Content-Type'] = 'application/json'
            return [200, response_headers, json.dumps(resp)]

        assert_pagination(pagination_function,
                          {'params': {'limit': str(limit), 'foo': 'bar'}},
                          request_handler,
                          lambda response: response.results,
                          "https://pagination.test/pagination/next_page_url",
                          expected_results, limit, Result)
