from onedict.merger import merge

openapi_example_1 = {
    "openapi": "3.0.0",
    "info": {"title": "Test API", "version": "1.0.0"},
    "tags": [
        {
            "name": "Test 1",
            "description": "Test 1 tag",
        }
    ],
    "paths": {
        "/test1": {
            "get": {
                "summary": "Test 1 endpoint",
                "tags": ["Test 1"],
                "responses": {"200": {"description": "Success"}},
            }
        }
    },
}

openapi_example_2 = {
    "openapi": "3.0.0",
    "info": {"title": "Test 2 API", "version": "1.0.0"},
    "tags": [
        {
            "name": "Test 2",
            "description": "Test 2 tag",
        }
    ],
    "paths": {
        "/test2": {
            "get": {
                "summary": "Test 2 endpoint",
                "tags": ["Test 2"],
                "responses": {"200": {"description": "Success"}},
            }
        }
    },
}

openapi_example_3 = {
    "openapi": "3.0.0",
    "info": {"title": "Test 3 API", "version": "1.0.0"},
    "paths": {
        "/test3": {
            "get": {
                "summary": "Test 3 endpoint",
                "responses": {"200": {"description": "Success"}},
            }
        },
    },
}


def test_merge_success():
    """Test merging two OpenAPI examples successfully."""
    expected_merged = {
        "openapi": "3.0.0",
        "info": {"title": "Test API & Test 2 API & Test 3 API", "version": "1.0.0"},
        "tags": [
            {
                "name": "Test 1",
                "description": "Test 1 tag",
            },
            {
                "name": "Test 2",
                "description": "Test 2 tag",
            },
        ],
        "paths": {
            "/test1": {
                "get": {
                    "summary": "Test 1 endpoint",
                    "tags": ["Test 1"],
                    "responses": {"200": {"description": "Success"}},
                }
            },
            "/test2": {
                "get": {
                    "summary": "Test 2 endpoint",
                    "tags": ["Test 2"],
                    "responses": {"200": {"description": "Success"}},
                }
            },
            "/test3": {
                "get": {
                    "summary": "Test 3 endpoint",
                    "responses": {"200": {"description": "Success"}},
                }
            },
        },
    }

    def on_conflict(keys, value1, value2):
        if keys == ["tags"]:
            assert isinstance(value1, list) and isinstance(value2, list)
            return value1 + [item for item in value2 if item not in value1]
        assert keys == ["info", "title"]
        return f"{value1} & {value2}"

    merged = merge(
        openapi_example_1,
        openapi_example_2,
        openapi_example_3,
        conflict_solvers=[on_conflict],
    )
    assert merged == expected_merged


def test_merge_conflict():
    """Test merging two OpenAPI examples with a conflict."""
    openapi_example_2_conflict = {
        "openapi": "3.0.0",
        "info": {"title": "Test API", "version": "1.0.1"},
        "paths": {
            "/demo": {
                "get": {
                    "summary": "Demo endpoint",
                    "responses": {"200": {"description": "Success"}},
                }
            }
        },
    }

    try:
        merge(openapi_example_1, openapi_example_2_conflict)
    except Exception as e:
        assert str(e) == "Conflict detected for key 'info.version': 1.0.0 != 1.0.1"
    else:
        assert False
