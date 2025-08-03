# Dynamic Expressions

Dynamic Expressions are a powerful mechanism for extracting, transforming, and evaluating data in request and responses.
They extend the concept of "runtime expressions" from the OpenAPI specification by introducing additional features to
handle complex data structures and perform evaluations.

Dynamic Expressions are primarily designed to provide a flexible way to define the behavior of pagination operations,
with potential for other applications in the future.

## Syntax Overview

### OpenAPI Runtime Expressions

Dynamic Expressions support the standard OpenAPI runtime expressions, which allow you to extract values from requests
and responses using a simple syntax.

Dynamic Expressions also support standard OpenAPI runtime expressions, which use `$` to extract values from requests and
responses.

**Syntax:**

```
$expression
```

**Examples:**

- `$request.query.limit` retrieves the `limit` query parameter from the request.
- `$response.body#/users/0/name` extracts the `name` of the first user from the response body.
- `$response.body#/cursors/has_more ?? false` returns the value of `has_more` from the response body,
  defaulting to `false` if it does not exist.

You can read more about OpenAPI runtime expressions in
the [OpenAPI Specification](https://swagger.io/docs/specification/v3_0/links/#runtime-expression-syntax).

### Dot-Separated Paths

Dot-separated paths provide a convenient way to access fields in nested data structures, such as JSON objects. These
paths always begin with a `#` and use dots (`.`) to navigate through nested fields.

When applied to an HTTP response object, the response body is used as the data structure.

**Syntax:**

```
#field.subfield
```

**Examples:**

- `#users.0.name` extracts the `name` of the first user in the `users` array.
- `#metadata.version` retrieves the `version` field from the `metadata` object.
- `#` retrieves the entire data structure.

### Compound Expressions

Curly braces allow you to combine multiple expressions or include literal text alongside evaluated expressions. This is useful for constructing strings dynamically.

Expressions within curly braces `{}` can use the nullish coalescing operator (`??`) to provide a default value if the expression evaluates to `null` or is undefined. This ensures a valid value is always available, even when the original expression yields no result.

**Syntax:**

```
{expression}
```

**Examples:**

- `Hello, {#users.0.name}!` evaluates to `Hello, Alice!` if the first user's name is `Alice`.
- `/books/{#book.id}/authors/{#author.id}` constructs a URL path using dynamic values.
- `{#users.0.age ?? 'unknown'}` evaluates to the first user's age, or `'unknown'` if the age is not available.



### Literals

Literals are treated as static values and are not evaluated. Any expression that does not start with `$` or `#` is
considered a literal.

**Syntax:**

```
Literal text
```

**Examples:**

- `Hello` remains as `Hello`.
- `42` remains as `42`.

### `$eval()` Expressions

`$eval()` allows you to perform complex evaluations, including mathematical operations, function calls, and combining
multiple values. Expressions are evaluated in a controlled manner, ensuring that arbitrary code execution is not
possible.

The current implementation supports:

- Basic arithmetic operations (addition `+`, subtraction `-`, multiplication `*`, division `/`).
- String concatenation using `+`.
- Comparison operators (`==`, `!=`, `<`, `>`, `<=`, `>=`).
- `false`, `true`, and `null` literals.
- Functions:
    - `int`: Converts a value to an integer.
    - `len`: Returns the length of a collection (e.g., array, string).
    - `round`: Rounds a number to the nearest integer.
    - `floor`: Rounds a number down to the nearest integer.
    - `ceil`: Rounds a number up to the nearest integer.

The current implementation is pretty basic and does not support complex operators or functions. Try to keep expressions
simple and straightforward.

**Syntax:**

```
$eval(expression)
```

**Examples:**

- `$eval(1 + 2)` evaluates to `3`.
- `$eval(len({#users}) + 1)` calculates the length of the `users` array and adds `1`.
- `$eval(int({$request.query.limit}) + len({$response.body#/data}))` combines values from the request and response to
  compute a new value.
- `$eval("Hello, " + {#users.0.name})` evaluates to `Hello, Alice!` if the first user's name is `Alice`.
- `$eval({#users.0.age} > 18)` evaluates to `True` if the first user is older than 18.

## Examples

As stated, Dynamic Expressions are primarily used in pagination operations to access and manipulate data from requests
and responses. Let's say we have the following HTTP request:

```http
GET https://api.example.com/books?limit=10&offset=20
X-API-Key: your_api_key
```

And the response to this request is:

```json
{
  "data": [
    {"id": 1, "title": "Book One"},
    {"id": 2, "title": "Book Two"}
  ],
  "cursors": {
    "next": "https://api.example.com/books?limit=10&offset=30"
  }
}
```

You can use Dynamic Expressions to access data from both the request and response:
- `$request.query.limit` retrieves the `limit` query parameter from the request: `10`.
- `$response.body#/cursors/next` extracts the next page URL from the response: `https://api.example.com/books?limit=10&offset=30`.
- `#data.0.title` retrieves the title of the first book in the response: `Book One`.
- `$eval({$request.query.offset} + len({$response.body#/data}))` calculates the new offset based on the number of items in the response: `22`.
- `$eval(len({#data}) > 0)` checks if there are any items in the response: `True`.
- `{{#data.0.title} ?? 'No title'}` retrieves the title of the first book, defaulting to "No title" if it does not exist: `Book One`.
