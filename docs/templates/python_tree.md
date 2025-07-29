# python-tree Template

The `python-tree` template is designed to generate Python client libraries with a hierarchical structure that reflects the organization of REST API endpoints.

It provides chainable methods that mirror the hierarchical nature of REST APIs. For example, an endpoint like `GET /accounts/<account>/users/<user>` can be accessed with a call such as `client.accounts(account).users(user).get()`. This design makes it straightforward to navigate and interact with nested resources in the API.

> 👀 The `python-tree` template generates Pydantic models to define request and response schemas. It relies heavily on the Content-Type values specified in the OpenAPI documentation to determine how to process request and response payloads. Therefore, ensuring the specification is accurate and complete is crucial for the output client to work as intended.

## Example usage
The generated client library allows you to interact with the API in a way that closely resembles the API's structure. Here's an example of how to use the generated client:

```python
from my_api_client import API
from my_api_client.security import BasicAuthentication
from my_api_client.models import EmployeeCreate

api = API(security_strategy=BasicAuthentication(username='user', password='pass'))

# Get a specific employee in a company
employee = api.companies("acme").employees(123).get()  # GET /companies/acme/employees/123
print(f"Employee Name: {employee.name}")

# Creates a new employee in the marketing department
req = EmployeeCreate(name="John Doe", position="Marketing Specialist")
new_employee = api.companies("acme").departments("marketing").employees().post(req)
print(f"New Employee ID: {new_employee.id}")
```

## Authentication

This template supports the following authentication methods:
- [**Basic Authentication**](https://swagger.io/docs/specification/v3_0/authentication/basic-authentication/): Used for simple username and password authentication.
- [**Bearer Authentication**](https://swagger.io/docs/specification/v3_0/authentication/bearer-authentication/): Used for token-based authentication, such as OAuth2 tokens.
- [**OAuth2**](https://swagger.io/docs/specification/v3_0/authentication/oauth2/): Supports the Client Credentials grant flow for OAuth2 authentication, including refresh token handling if specified in the OpenAPI specification.

To use authentication, you need to specify the security strategy when creating the API client instance. The client will automatically handle authentication for each request based on the provided security configuration.
```python
from my_api_client import API
from my_api_client.security import BasicAuthentication, BearerToken, OAuth2ClientCredentials

# Basic Authentication
api1 = API(security_strategy=BasicAuthentication(username='user', password='pass'))

# Bearer Token Authentication
api2 = API(security_strategy=BearerToken(token='your_token_here'))

# OAuth2 Client Credentials Authentication
api3 = API(security_strategy=OAuth2ClientCredentials(
    client_id='your_client_id',
    client_secret='your_client_secret',
    scopes=['read', 'write']
))
```

The security strategies are named based on the OpenAPI specification and should align with the security schemes defined in your OpenAPI document.

### Authentication with Scoped Context

You can use context managers to automatically handle token revocation for OAuth2 authentication. When the context is exited, the token is revoked, ensuring secure and clean resource management.

```python
from my_api_client import API
from my_api_client.security import OAuth2ClientCredentials

with API(security_strategy=OAuth2ClientCredentials(client_id='your_client_id',
                                                   client_secret='your_client_secret',
                                                   scopes=['read', 'write'])) as api:
# Perform API calls within the context
    employee = api.companies("acme").employees(123).get()
print(f"Employee Name: {employee.name}")
```


## Supported Extensions

The `python-tree` template supports the following OpenAPI extensions to enhance the generated client. For detailed descriptions, refer to the [OpenAPI extensions documentation](../extensions/README.md):
- [Template Configuration](../extensions/README.md#template-configuration) (`x-apier.templates`)
- [Equivalent Paths](../extensions/README.md#equivalent-paths) (`x-apier.equivalent-paths`)
- [Pagination](../extensions/README.md#pagination) (`x-apier.pagination`)
- [Method Name](../extensions/README.md#method-name) (`x-apier.method-name`)
- [Input Parameters](../extensions/README.md#input-parameters) (`x-apier.input-parameters`)
- [Response Stream](../extensions/README.md#response-stream) (`x-apier.response-stream`)

### Template Configuration

This template supports the following template configuration options:
- `raise-response-errors`: When set to `true`, the client raises a `ResponseError` for non-2xx responses. If set to `false`, the client returns the raw response object, allowing you to handle errors manually. The default value is `true`.

Configuration example:
```yaml
info:
  x-apier:
    templates:
      python-tree:
        raise-response-errors: true  # Enable raising exceptions for non-2xx responses
```

### Pagination

The `python-tree` template currently supports cursor and url pagination, allowing you to navigate through large datasets efficiently. The pagination is handled automatically by the generated client, so you can iterate over results without worrying about the underlying pagination logic.

Example:
```python
# List all companies
company_list = api.companies().list()

# Iterate over all companies, handling pagination automatically
for company in company_list:
    print(f"Company Name: {company.name}")
```

## Inspecting HTTP Response Details

All the objects returned by a client method have a `http_response()` method that returns the raw HTTP response object as a `requests.Response` instance. This allows you to inspect the response details, such as headers, status code, and body content.

Example:
```python
resp = api.companies("acme").employees(123).get()
print(f"Response Status Code: {resp.http_response().status_code}")
```

## Error Handling

The `python-tree` template provides built-in support for handling errors that may occur during API calls. When the `raise-response-errors` configuration option is set to `true`, the client will raise errors as instances of `ResponseError`.

Like response objects, `ResponseError` instances have a `http_response()` method to access the raw HTTP response details.

The following example demonstrates how to handle errors when making API calls:

```python
from my_api_client import API
from my_api_client.models.exceptions import ResponseError

api = API()

try:
    # Attempt to fetch an employee
    employee = api.companies("acme").employees(123).get()
    print(f"Employee Name: {employee.name}")
except ResponseError as e:
    print(f"An error occurred: {e}")
    # Access the raw HTTP response
    raw_response = e.http_response()
    print(f"Response Status Code: {raw_response.status_code}")
    print(f"Response Body: {raw_response.text}")
```

## Multipart Requests

The `python-tree` template supports multipart requests for endpoints that require file uploads or other multipart data. By default, `requests` library will handle multipart encoding by loading the full request body into memory. This can be a problem for large files or datasets.

The [`requests-toolbelt`](https://github.com/requests/toolbelt) library enables streaming multipart requests. Simply add `requests-toolbelt` to your api library dependencies, and the generated client will automatically use it to handle multipart requests.

The `FilePayload` class is the recommended way to handle file uploads in multipart requests. It allows you to set the file content and metadata, such as filename and content type, or load the file content from a given file path.

### Example

Let's say you have an OpenAPI schema that defines an endpoint for uploading books:
```yaml
components:
  schemas:
    BookUploadRequest:
      type: object
      required:
        - title
        - file
      properties:
        title:
          type: string
        author:
          type: string
        publication_year:
          type: integer
        file:
          type: string
          format: binary  # This is needed for file uploads
```

In the above schema, the `file` property is defined as a binary type, which indicates that it will be used for file uploads. The generated client will create a model for this request:

```python
class BookUploadRequest(APIBaseModel):
    title: str
    author: Optional[str] = None
    publication_year: Optional[int] = None
    file: Union[bytes | IO | IOBase | FilePayload]
```

This model accepts a `FilePayload` instance for the `file` field, which can be used to upload a file as part of a multipart request. Note that you can also set the `file` field to a byte string or an IO object, but using `FilePayload` is recommended for better handling of file metadata, such as filename and content type.

You can create a `FilePayload` instance like this and use it in your request:

```python
from my_api_client import API
from my_api_client.models.primitives import FilePayload

book_req = BookUploadRequest(
    title="The Great Gatsby",
    author="F. Scott Fitzgerald",
    publication_year=1925,
    file=FilePayload(
        content=open("my_library/great_gatsby.pdf", "rb"),
        filename="great_gatsby.pdf",
        content_type="application/pdf"
    )
)

resp = API().books().post(book_req)  # POST /books/upload
```

Alternatively, you can also use the `FilePayload.from_path` method to create a `FilePayload` instance from a file path, which automatically sets the filename and content type based on the file's properties:

```python
book_req = BookUploadRequest(
    title="The Great Gatsby",
    author="F. Scott Fitzgerald",
    publication_year=1925,
    file=FilePayload.from_path("my_library/great_gatsby.pdf")
)
```

## Binary Responses

When dealing with binary responses, such as images or files, the generated client will automatically decode the response and fit it into a `FilePayload` instance in the response model.

The response's content type must match the exact type of the binary data being returned, such as `image/png` or `application/pdf`. Alternatively, you can use `*/*` to indicate that the response may contain any type of binary data. Other content types might not work as expected.

By default, the response is fully loaded into memory. To process large binary responses efficiently, set the `stream` parameter to `True` when making the request to enable chunked processing without loading the entire response into memory. Alternatively, you can use the `x-apier.response-stream` extension to change the default stream behavior for the response body.

### Example

Let's imagine you have an OpenAPI endpoint that expects a binary response:
```yaml
paths:
  /books/{book_id}/download:
    get:
      summary: Download a book
      parameters:
        - name: book_id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Successful response with binary data
          content:
            application/pdf:
              schema:
                type: string
                format: binary  # This is needed for binary responses
```

The generated client will create a model for the response that expects a FilePayload instance:
```python
class BooksBookIdDownloadResponse200(APIBaseModel):
    __root__: Union[bytes | IO | IOBase | FilePayload]
```

After a successful request, you can access the binary data by reading the content of the `FilePayload` instance:

```python
from my_api_client import API

resp = API().books("123").download().get(stream=True)  # GET /books/123/download

file_payload = resp.__root__
with open(file_payload.filename, "wb") as f:
    while chunk := file_payload.content.read():
        f.write(chunk)
```

Alternatively, you can also read the content directly from the HTTP response object accessed via the `http_response()` method.

In the example above, the `stream=True` parameter is used to enable streaming of the response content. This allows you to read the binary data in chunks, which is particularly useful for large files. When `stream=False`, the full response is loaded into memory, and the `content` field of the `FilePayload` instance contains a `bytes` object instead of an IO stream.

## ⚠️ Limitations

- 🧬 The `python-tree` template is best suited for APIs that have a clear hierarchical structure. It may not be the best choice for APIs with flat or complex endpoint structures, where a different template design might be more appropriate.
- 💾 **Request payloads**: This template supports request payloads with content types such as `text/plain`, `application/json`, `application/xml`, `multipart/form-data`, and `application/x-www-form-urlencoded`. Other content types are untested and may not be supported.
- 📦 **Response payloads**: Supports response content types like `text/plain`, `application/json`, `application/xml`, and binary data.
- 🧭 Strategies requiring dynamic evaluation of runtime expressions, such as page or offset pagination, are not yet supported.