# python-tree Template

The `python-tree` template is designed to generate Python client libraries with a hierarchical structure that reflects the organization of REST API endpoints.

It provides chainable methods that mirror the hierarchical nature of REST APIs. For example, an endpoint like `GET /accounts/<account>/users/<user>` can be accessed with a call such as `client.accounts(account).users(user).get()`. This design makes it straightforward to navigate and interact with nested resources in the API.

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
- **`x-apier.templates`**
- **`x-apier.equivalent-paths`**
- **`x-apier.pagination`**
- **`x-apier.method-name`**
- **`x-apier.input-parameters`**

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

## ⚠️ Limitations

- 🧬 The `python-tree` template is best suited for APIs that have a clear hierarchical structure. It may not be the best choice for APIs with flat or complex endpoint structures, where a different template design might be more appropriate.
- 💾 Only text, JSON, and XML payloads are supported for requests and responses. Binary payloads, such as file uploads, are not supported yet.
- 🧭 Strategies requiring dynamic evaluation of runtime expressions, such as page or offset pagination, are not yet supported.