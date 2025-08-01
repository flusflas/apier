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
            result: "results"
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
        result: "results"
        has_more: "$response.body#/next_page_url"
```

## Pagination Extension Attributes

The following attributes are supported in the pagination extension. Most fields accept [OpenAPI Runtime Expressions](https://swagger.io/docs/specification/v3_0/links/#runtime-expression-syntax) or dot-separated paths to extract values from the request or response.

| Attribute                | Type      | Description                                                                                       |
|--------------------------|-----------|---------------------------------------------------------------------------------------------------|
| `reuse_previous_request` | boolean   | If true, the next request reuses the previous request's parameters.                               |
| `modifiers`              | array     | List of request modifiers to update parameters for the next request.                              |
| `param` (modifier)       | string    | The request parameter to modify (e.g., `$request.query.next`).                                    |
| `value` (modifier)       | string    | Runtime expression to extract the value for the modifier.                                         |
| `url`                    | string    | Runtime expression to extract the next page URL from the response.                                |
| `result`                 | string    | Runtime expression or path to extract the data results from the response.                         |
| `has_more`               | string    | Runtime expression indicating if more pages are available.                                        |

### Runtime Expressions

[OpenAPI Runtime Expressions](https://swagger.io/docs/specification/v3_0/links/#runtime-expression-syntax) allow you to dynamically extract values from the request or response. In pagination configurations, they are used to specify how to retrieve the next page's cursor or URL, identify the result set, and determine if more pages are available, among other uses.

In addition to the standard OpenAPI runtime expressions, apier also supports some additional features:
- **Dot-separated paths** (e.g., `cursors.next`) can be used as a shortcut to access fields in the response body.
- **Curly braces** can be used to include multiple runtime expressions in a single field (e.g., `/books/{$request.path.book_id}/authors/{$request.path.author_id}`).

### Request Modifiers

Request modifiers let you update request parameters for the next page based on values from the previous request or response. Modifiers are defined as an array of objects, each specifying a parameter to modify and the value to set it to.
- **param**: The request parameter to modify (e.g., `$request.query.next`). Here, `$request` refers to the request being prepared to fetch the next page.
- **value**: A runtime expression that extracts the value from the previous response or request. This value will be used to update the specified parameter for the next request. In this context, `$response` refers to the response from the previous request, and `$request` refers to the previous request.

The following example shows how to use a runtime expression to extract the next cursor value from the response body (`$response.body#/cursors/next`) and use it to update the `next` query parameter (`$request.query.next`) for the next request:

```yaml
x-apier:
  pagination:
    next:
      reuse_previous_request: true
      modifiers:
        - param: "$request.query.next"
          value: "$response.body#/cursors/next"
      result: "results"
      has_more: "$response.body#/cursors/next"
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
      result: "results"
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
      url: "$response.body#/next_page_url"
      result: "results"
      has_more: "$response.body#/next_page_url"
```

### Offset and Page Number Pagination
Offset and page number strategies need more complex expression evaluation. For example:
- `$eval({$request.query.page} + 1)` to increment the page number.
- `$eval({$request.query.offset} + len({$response.body#/data}))` to increment the offset based on the number of items in the current response.
- `$eval(len({$response.body#/data}) >= {$request.query.limit})` to determine if there are more pages based on the number of items returned.

This is still a work in progress, and you could expect to be available soon.
