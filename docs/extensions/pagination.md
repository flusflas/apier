# Pagination Extension

This document describes the `x-apier.pagination` extension for OpenAPI specifications. This extension allows you to define how paginated endpoints should be handled by generated clients, supporting a variety of pagination strategies found in APIs.

The pagination extension provides a flexible approach to handling various pagination strategies used by APIs. It defines how to fetch the next page of results, update the request for subsequent pages, and extract results from the response. This enables the generated client to manage pagination automatically, reducing the need for manual intervention by developers.

The extension is designed to support the following main pagination strategies commonly used by APIs:
- **Cursor Pagination**: Uses a cursor value (e.g., a token or ID) to retrieve the next page of results.
- **Next Page URL Pagination**: Uses a URL provided in the response to fetch the next page.
- **Page Pagination**: Uses a page number and limit to determine the next set of results. 🚧 Implementation is in progress.
- **Offset Pagination**: Uses an offset value to specify the starting point for the next page of results. 🚧 Implementation is in progress.

## Specifying Pagination in OpenAPI

The pagination extension is added under the `x-apier.pagination` field in an operation object. You can define the configuration directly (in-place) or reference a shared definition using `$ref`.

### In-place Example
```yaml
paths:
  /pagination/cursor:
    get:
      # ...
      x-apier:
        pagination:
          next:
            reuse_previous_request: true
            modifiers:
              - param: "$request.query.next"
                value: "$response.body#/cursors/next"
            result: "#results"
            has_more: "$response.body#/cursors/next"
```

### Using $ref
```yaml
paths:
  /pagination/next_page_url:
    get:
      # ...
      x-apier:
        pagination:
          $ref: '#/components/x-pagination/PagePagination'

components:
  x-pagination:
    PagePagination:
      next:
        reuse_previous_request: true
        url: "$response.body#/next_page_url"
        result: "#results"
        has_more: "$response.body#/next_page_url"
```

## Pagination Extension Configuration

Pagination in apier can be configured in two main ways: **Modifiers-based Pagination** and **Operation-based Pagination**. Each approach is suited to different API designs and use cases.

> 🧙‍♂️ **Using Dynamic Expressions**: Most pagination attributes accept [Dynamic Expressions](./expressions.md), which are a superset of OpenAPI Runtime Expressions. They allow you to extract and manipulate values from the request or response, combine multiple expressions, and perform advanced evaluations.

### 1. Modifiers-based Pagination

Use this approach when you need to update the parameters of the next request based on the previous response or request. Modifiers allow you to dynamically adjust query parameters, headers, or other request fields to fetch the next page.

| Attribute                | Type    | Required | Description                                                                                                                                                  |
|--------------------------|---------|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `reuse_previous_request` | boolean | False    | If true, the next request reuses the previous request's parameters.                                                                                          |
| `modifiers`              | array   | False    | List of request modifiers to update parameters for the next request. Each modifier specifies which parameter to update and how to extract its new value.     |
| `result`                 | string  | True     | [Dynamic Expression](./expressions.md) or path to extract the data results from the response.                                                                |
| `has_more`               | string  | True     | [Dynamic Expression](./expressions.md) that determines if additional pages are available. If the evaluated result is `false` or empty, pagination will stop. |

If `reuse_previous_request` is not set, the next request will default to the same URL and method as the previous one, unless the modifiers specify otherwise.

Modifiers define how to update the next request based on the previous response. Each modifier specifies which request parameter to change and how to compute its new value:

| Attribute | Type   | Description                                                                   |
|-----------|--------|-------------------------------------------------------------------------------|
| `param`   | string | The request parameter to modify (e.g., `$request.query.next`).                |
| `value`   | string | [Dynamic Expression](./expressions.md) to extract the value for the modifier. |

**Example:**
```yaml
x-pagination:
  next:
    reuse_previous_request: true
    modifiers:
      - param: $request.query.page
        value: "$response.body#/next_page"
    result: "#results"
    has_more: "$response.body#/next_page"
```

### 2. Operation-based Pagination

Use this approach when the next page should be fetched by invoking a different or specific OpenAPI operation, rather than modifying the current request.

This pagination mode could be useful for non-standard pagination strategies where the next page is determined by a separate operation.

| Attribute      | Type   | Required | Description                                                                                                                                                  |
|----------------|--------|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `operation_id` | string | Yes      | Defines the OpenAPI operation to fetch the next page.                                                                                                        |
| `parameters`   | array  | No       | Parameters to pass to the operation. This allows you to specify any parameters required by the operation, such as path or query parameters.                  |
| `result`       | string | Yes      | [Dynamic Expression](./expressions.md) or path to extract the data results from the response.                                                                |
| `has_more`     | string | Yes      | [Dynamic Expression](./expressions.md) that determines if additional pages are available. If the evaluated result is `false` or empty, pagination will stop. |

Parameters can be specified to pass values to the operation. If the operation requires specific parameters, they need to be defined here or the operation will fail.

| Attribute | Type   | Description                                                                                                 |
|-----------|--------|-------------------------------------------------------------------------------------------------------------|
| `name`    | string | The name of the parameter to pass to the operation. This should match the operation's parameter definition. |
| `value`   | string | [Dynamic Expression](./expressions.md) to extract the value for the parameter.                              |

**Example:**
```yaml
x-pagination:
  operation_id: getNextPage  (e.g. GET /items/{cursor-id})
  parameters:
    - name: "cursor-id"  # The required 'cursor-id' parameter
      value: "$response.body#/next_id"
  result: "#items"
  has_more: "$response.body#/next_id"
```

## Supported Pagination Strategies (Use Cases)

While every API may have its own specific requirements and implement pagination differently, the extension should be flexible enough to cover most use cases. Below are examples of how to configure the extension for different pagination strategies.

### Cursor Pagination
Uses a value (cursor) returned in the response to fetch the next page. The client updates the request with the new cursor value for each subsequent request.

**Example:**
```yaml
x-apier:
  pagination:
    next:
      reuse_previous_request: true
      modifiers:
        - param: "$request.query.next"
          value: "$response.body#/cursors/next"
      result: "#results"
      has_more: "$response.body#/cursors/next"
```

### Next Page URL Pagination
Uses a URL provided in the response to fetch the next page. The client follows the URL for each subsequent request.

**Example:**
```yaml
x-apier:
  pagination:
    next:
      reuse_previous_request: true
      modifiers:
        - param: "url"
          value: "$response.body#/next_page_url"  # Update the request URL with the next page URL
      result: "#results"
      has_more: "$response.body#/next_page_url"
```

### Offset Pagination
Uses an offset value to specify the starting point for the next page of results. The client updates the request with the new offset value based on the number of items returned in the previous response.

**Example:**
```yaml
x-apier:
  pagination:
    next:
      reuse_previous_request: true
      modifiers:
        - param: "$request.query.offset"
          value: "$eval({$request.query.offset ?? 0} + len({#results}))"  # Increment offset by the number of results returned
      result: "#results"
      has_more: "$eval(len({$response.body#/results}) >= {$request.query.limit})"  # Keep fetching if the number of results is equal to the limit
```

### Page Number Pagination
Uses a page number and limit to determine the next set of results. The client updates the request with the new page number for each subsequent request.

**Example:**
```yaml
x-apier:
  pagination:
    next:
      reuse_previous_request: true
      modifiers:
        - param: "$request.query.page"
          value: "$eval({$request.query.page ?? 0} + 1)"  # Increment page number by 1
      result: "#results"
      has_more: "$eval(len({$response.body#/results}) >= {$request.query.page_size})"  # Keep fetching if the number of results is equal to the page size
```
