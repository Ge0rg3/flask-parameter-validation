# Flask Parameter Validation

**Get and validate all Flask input parameters with ease.**

Flask Parameter Validation lets you declare a route's expected inputs directly in the
function signature using type hints and `Parameter` defaults. Inputs are then automatically
extracted, type-checked, validated against the constraints you specify, and passed to your
view. As a bonus, the same declarations are used to generate OpenAPI 3.1 documentation.

```py
@app.route("/users/<int:id>", methods=["POST"])
@ValidateParameters()
def update_user(
        id: int = Route(),
        username: str = Json(min_str_length=5, blacklist="<>"),
        age: int = Json(min_int=18, max_int=99),
        is_admin: bool = Query(False),
):
    ...
```

## Features

- Declarative validation via type hints and `Parameter` defaults — no boilerplate parsing.
- Input sources: `Route`, `Query`, `Json`, `Form`, `File`, and `MultiSource`.
- Rich type support: primitives, `datetime`/`date`/`time`, `UUID`, `Enum`, `list`, `dict`,
  `TypedDict`, `Union`/`Optional`, and more.
- Constraints: length/range bounds, regex patterns, character white/blacklists, JSON Schema,
  and fully custom validation functions.
- Customisable error responses.
- Automatic API documentation: OpenAPI 3.1 (with 3.2 compatibility) plus a built-in HTML docs page.
- Supports both sync and async views; tested on Python 3.9–3.13.

## Install

```sh
pip install flask_parameter_validation
```

Or from source:

```sh
git clone https://github.com/Ge0rg3/flask-parameter-validation.git
cd flask-parameter-validation
pip install .
```

## Quick start

```py
from flask import Flask
from flask_parameter_validation import ValidateParameters, Route, Json, Query

app = Flask(__name__)

@app.route("/users/<int:id>", methods=["POST"])
@ValidateParameters()
def update_user(
        id: int = Route(),
        username: str = Json(min_str_length=5),
        age: int = Json(min_int=18, max_int=99),
        is_admin: bool = Query(False),
):
    return {"id": id, "username": username, "age": age, "is_admin": is_admin}

if __name__ == "__main__":
    app.run()
```

A request to this route, supplying `id` via the path, `is_admin` via the query string, and
`username`/`age` via the JSON body:

```sh
curl -X POST "http://localhost:5000/users/42?is_admin=true" \
     -H "Content-Type: application/json" \
     -d '{"username": "alice123", "age": 30}'
```

```json
{"id": 42, "username": "alice123", "age": 30, "is_admin": true}
```

Two conditions must be met for a route to be validated:

1. The `@ValidateParameters()` decorator is applied to the view function.
2. Each validated argument has a [type hint](#supported-types) and a default that is an
   instance of a [`Parameter` subclass](#parameter-sources).

## Parameter sources

Each input source is a subclass of `Parameter`:

| Subclass      | Input source                                                                | Available for                   |
|---------------|-----------------------------------------------------------------------------|---------------------------------|
| `Route`       | A value in the URL path, e.g. `/users/<int:id>`                             | All HTTP methods                |
| `Query`       | A value in the URL query string, e.g. `/articles?id=55`                    | All HTTP methods                |
| `Json`        | A value in the JSON request body (`Content-Type: application/json`)         | Body methods (POST/PUT/PATCH/…) |
| `Form`        | A value in an HTML form / `FormData` body (`x-www-form-urlencoded`)         | Body methods (POST/PUT/PATCH/…) |
| `File`        | An uploaded file in the request body                                        | Body methods (POST/PUT/PATCH/…) |
| `MultiSource` | A value from any combination of the sources above                           | Depends on chosen sources       |

> "Body methods" are the HTTP methods that carry a request body — POST, PUT, PATCH and DELETE.
> Sending a body via DELETE is non-standard, but Flask and this library support it.

### MultiSource parameters

`MultiSource` accepts a value from any combination of the other sources, tried in order:

```py
from flask_parameter_validation import ValidateParameters, MultiSource, Route, Query, Json

@app.route("/")
@app.route("/<value>")  # Register paths with and without the Route parameter
@ValidateParameters()
def multi_source_example(
        value: int = MultiSource(Route, Query, Json, min_int=0)
):
    return {"value": value}
```

## Supported types

Type hints declare the expected Python type of each parameter. Some types are only available
to certain sources.

| Type hint                                       | Notes                                                                                          | `Route` | `Form` | `Json` | `Query` | `File` |
|-------------------------------------------------|------------------------------------------------------------------------------------------------|:-------:|:------:|:------:|:-------:|:------:|
| `str`                                           |                                                                                                |    Y    |   Y    |   Y    |    Y    |   N    |
| `int`                                           |                                                                                                |    Y    |   Y    |   Y    |    Y    |   N    |
| `bool`                                          |                                                                                                |    Y    |   Y    |   Y    |    Y    |   N    |
| `float`                                         |                                                                                                |    Y    |   Y    |   Y    |    Y    |   N    |
| `list` / `typing.List`                          | See [list parsing](#list-parsing) for how values are received per source.                      |    N    |   Y    |   Y    |    Y    |   N    |
| `dict`                                          | For `Query`/`Form`, pass stringified JSON (usually with `list_disable_query_csv=True`).        |    N    |   Y    |   Y    |    Y    |   N    |
| `TypedDict`                                     | As `dict`, with per-key type validation.                                                       |    N    |   Y    |   Y    |    Y    |   N    |
| `typing.Union`                                  |                                                                                                |    Y    |   Y    |   Y    |    Y    |   N    |
| `typing.Optional`                               | Not supported for `Route`.                                                                      |    Y    |   Y    |   Y    |    Y    |   Y    |
| `datetime.datetime`                             | Received as an ISO-8601 date-time string.                                                       |    Y    |   Y    |   Y    |    Y    |   N    |
| `datetime.date`                                 | Received as an ISO-8601 full-date string.                                                        |    Y    |   Y    |   Y    |    Y    |   N    |
| `datetime.time`                                 | Received as an ISO-8601 partial-time string.                                                     |    Y    |   Y    |   Y    |    Y    |   N    |
| `enum.Enum` (with `str`/`int` mixin or sub)     | `StrEnum`/`IntEnum`, or `str, Enum` / `int, Enum` prior to Python 3.11.                          |    Y    |   Y    |   Y    |    Y    |   N    |
| `uuid.UUID`                                     | Received as a `str`, with or without hyphens, case-insensitive.                                 |    Y    |   Y    |   Y    |    Y    |   N    |
| `werkzeug.datastructures.FileStorage`           |                                                                                                |    N    |   N    |   N    |    N    |   Y    |

### List parsing

- **`Json`**: received as a JSON list.
- **`Query`**: `value=1,2,3` if `list_disable_query_csv` is `False` (the default), or
  `value=1&value=2&value=3`.
- **`Form`**: `value=1&value=2&value=3`.
- A single `value=` with no value always becomes an empty list; `value=,` (`Query`) and
  `value=&value=` become a list of empty strings.
- Lists that accept `None` as a member type are only supported for `Json`.

## Validation constraints

Pass constraints as keyword arguments to a `Parameter` subclass. Each constraint applies only
to certain types:

| Argument                 | Type                                             | Applies to             | Description                                                                 |
|--------------------------|--------------------------------------------------|------------------------|-----------------------------------------------------------------------------|
| `default`                | any (except `None`)                              | All except `Route`     | Default value; makes a non-`Optional` field not required.                   |
| `min_str_length`         | `int`                                            | `str`                  | Minimum string length.                                                       |
| `max_str_length`         | `int`                                            | `str`                  | Maximum string length.                                                       |
| `min_list_length`        | `int`                                            | `list`                 | Minimum number of list elements.                                             |
| `max_list_length`        | `int`                                            | `list`                 | Maximum number of list elements.                                             |
| `min_int`                | `int`                                            | `int`                  | Minimum value.                                                               |
| `max_int`                | `int`                                            | `int`                  | Maximum value.                                                               |
| `whitelist`              | `str`                                            | `str`                  | String of allowed characters.                                                |
| `blacklist`              | `str`                                            | `str`                  | String of forbidden characters.                                              |
| `pattern`                | `str`                                            | `str`                  | Regex pattern the value must match.                                          |
| `func`                   | `Callable[[Any], bool \| tuple[bool, str]]`      | All                    | [Custom validation function](#custom-validation-functions).                 |
| `datetime_format`        | `str`                                            | `datetime.datetime`    | `strptime` format string overriding ISO-8601 parsing.                       |
| `comment`                | `str`                                            | All                    | Description used in generated documentation.                                 |
| `alias`                  | `str`                                            | All except `File`      | Accept this parameter name instead of the function argument name.            |
| `json_schema`            | `dict`                                           | All except `File`      | [JSON Schema](https://json-schema.org) the value must conform to.            |
| `content_types`          | `list[str]`                                      | `File`                 | Allowed `Content-Type`s.                                                      |
| `min_length`             | `int`                                            | `File`                 | Minimum `Content-Length`.                                                     |
| `max_length`             | `int`                                            | `File`                 | Maximum `Content-Length`.                                                     |
| `blank_none`             | `bool`                                           | `Optional[str]`        | Convert an empty string to `None`. Defaults to `FPV_BLANK_NONE`.            |
| `list_disable_query_csv` | `bool`                                           | `list` in `Query`      | If `False`, split query lists on `,`. Defaults to `FPV_LIST_DISABLE_QUERY_CSV`. |

Examples:

```py
username: str = Json(default="anonymous", min_str_length=5)
profile_picture: FileStorage = File(content_types=["image/png", "image/jpeg"])
search: str = Query()
```

### Custom validation functions

Pass a callable to `func`. It receives the value and returns either a `bool`, or a
`(bool, error_message)` tuple:

```py
def is_even(value: int):
    return value % 2 == 0

def is_odd(value: int):
    return value % 2 != 0, "value must be odd"

count: int = Json(func=is_even)
```

### JSON Schema validation

```py
json_schema = {
    "type": "object",
    "required": ["user_id", "first_name", "last_name", "tags"],
    "properties": {
        "user_id": {"type": "integer"},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
    },
}

@app.post("/json_schema_example")
@ValidateParameters()
def json_schema_example(data: dict = Json(json_schema=json_schema)):
    return {"data": data}
```

## Error handling

By default, validation failures return a JSON response with the message in the `error` field:

```json
{ "error": "Parameter 'age' must be type 'int'" }
```

Pass a custom handler to `ValidateParameters()` to change the format:

```py
def error_handler(err):
    return {
        "error_name": type(err).__name__,
        "error_parameters": err.args,
        "error_message": str(err),
    }, 400

@app.route(...)
@ValidateParameters(error_handler)
def api(...):
    ...
```

## Configuration

Set these keys in `app.config`:

### API documentation

| Key                  | Type   | Description                                                                                  |
|----------------------|--------|----------------------------------------------------------------------------------------------|
| `FPV_OPENAPI_ENABLE` | `bool` | Enable OpenAPI generation. Must be truthy for the `/docs/openapi` route.                      |
| `FPV_OPENAPI_BASE`   | `dict` | Base [OpenAPI Object](https://spec.openapis.org/oas/v3.1.0#openapi-object); its `paths` is populated automatically. |

### Validation behaviour

| Key                          | Type   | Default | Description                                          |
|------------------------------|--------|---------|------------------------------------------------------|
| `FPV_BLANK_NONE`             | `bool` | `False` | Default `blank_none` behaviour for all routes.       |
| `FPV_LIST_DISABLE_QUERY_CSV` | `bool` | `False` | Default `list_disable_query_csv` behaviour.          |

### Legacy HTML docs (deprecated, non-standard format)

| Key                       | Type    | Default  | Description                                       |
|---------------------------|---------|----------|---------------------------------------------------|
| `FPV_DOCS_SITE_NAME`      | `str`   | `Site`   | Page title for the HTML docs.                     |
| `FPV_DOCS_CUSTOM_BLOCKS`  | `list`  | `[]`     | Cards shown at the top of the docs page.          |
| `FPV_DOCS_DEFAULT_THEME`  | `str`   | `light`  | Default theme for the HTML docs page.             |

## API documentation

Register the bundled blueprint to expose generated documentation:

```py
from flask_parameter_validation.docs_blueprint import docs_blueprint

app.config["FPV_OPENAPI_ENABLE"] = True
app.config["FPV_OPENAPI_BASE"] = {"openapi": "3.1.0"}
app.register_blueprint(docs_blueprint)
```

The blueprint is mounted at `/docs` and adds three `GET` routes:

- `/docs/` — an HTML documentation page (Bootstrap, light/dark mode).
- `/docs/openapi` — the OpenAPI 3.1 document as JSON.
- `/docs/json` — a non-standard JSON representation (deprecated).

To generate documentation without the blueprint:

```py
from flask_parameter_validation.docs_blueprint import (
    get_route_docs,              # non-standard format (deprecated)
    generate_openapi_paths_object,  # just the OpenAPI Paths object
    generate_openapi_docs,       # the full OpenAPI document
)
```

### Documenting routes

- The route's **docstring** becomes the OpenAPI Operation `description`.
- Parameter descriptions are resolved in priority order: a `Parameter`'s `comment` argument,
  then `Annotated[T, "..."]` / `# inline comment` on a `TypedDict` or `Enum` member, then a
  class docstring.
- Mark a route deprecated with `warnings.deprecated` (Python 3.13+) or
  `typing_extensions.deprecated`.
- Pass `openapi_responses` to `ValidateParameters()` to document a route's responses.

## Contributing

Contributions are welcome. See [AGENTS.md](AGENTS.md) for the project layout, how to run the
test suite, and coding conventions.

Many thanks to all those who have contributed:

- [d3-steichman](https://github.com/d3-steichman) / [smt5541](https://github.com/smt5541): API documentation, custom error handling, datetime validation and bug fixes
- [willowrimlinger](https://github.com/willowrimlinger): TypedDict support, dict subtyping, and async view handling bug fixes
- [summersz](https://github.com/summersz): parameter aliases, async support, form type conversion and list bug fixes
- [Garcel](https://github.com/Garcel): custom validator functions
- [iml1111](https://github.com/iml1111): regex validation
- [borisowww](https://github.com/borisowww): file handling bug fixes
- [Charlie-Mindified](https://github.com/Charlie-Mindified): JSON handling bug fix
- [dkassen](https://github.com/dkassen): list parsing fixes

## License

Released under the MIT License.
