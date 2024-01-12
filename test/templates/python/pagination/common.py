import copy
import math

import httpretty


@httpretty.activate
def assert_pagination(pagination_function: callable,
                      function_params: dict,
                      request_handler: callable,
                      get_response_data: callable,
                      expected_url: str,
                      expected_results: list,
                      expected_limit: int,
                      expected_type):
    """
    Asserts that, given API function (pagination_function) that supports
    pagination, it can be paginated properly.
    """
    httpretty.register_uri(httpretty.GET, expected_url, body=request_handler)
    function_params_copy = copy.deepcopy(function_params)

    actual_result = pagination_function(**function_params_copy)

    assert len(httpretty.latest_requests()) == 1
    if expected_limit < len(expected_results):
        assert len(get_response_data(actual_result)) == expected_limit
        # assert actual_result.has_more()
    else:
        assert len(get_response_data(actual_result)) == len(expected_results)
        # assert not actual_result.has_more()

    # Iterate results
    for result_index, result in enumerate(actual_result):
        assert result == expected_type.parse_obj(expected_results[result_index])

    # assert not actual_result.has_more()

    # Assert that the API has been called until all data has been fetched
    assert len(httpretty.latest_requests()) == math.ceil(len(expected_results) / expected_limit)
