# AGENTS.md

Guidance for coding agents working in this repository. For user-facing usage docs, see
[README.md](README.md).

## Project overview

`flask-parameter-validation` is a Flask extension that validates route inputs declared as type
hints with `Parameter` defaults in the view signature, and generates OpenAPI 3.1 documentation
from the same declarations. It is a published PyPI package (`Flask-Parameter-Validation`).

- Language: Python, supporting 3.9–3.13.
- Runtime dependencies: `Flask`, `flask[async]`, `python-dateutil`, `jsonschema`.
- Packaging: `setup.py` (setuptools). Version is the `version=` field there.
- License: MIT.

## Repository layout

```
flask_parameter_validation/        # The package
├── __init__.py                    # Public API: ValidateParameters + parameter types
├── parameter_validation.py        # @ValidateParameters decorator; input extraction + dispatch
├── docs_blueprint.py              # /docs blueprint + OpenAPI / legacy-JSON generation
├── parameter_types/               # One module per input source
│   ├── parameter.py               # Base Parameter class; core validation logic
│   ├── route.py  query.py  json.py  form.py  file.py
│   └── multi_source.py            # MultiSource (accepts a value from several sources)
├── exceptions/exceptions.py       # MissingInputError, InvalidParameterTypeError,
│                                  #   ValidationError, ConfigurationError
├── templates/fpv_default_docs.html# HTML docs page rendered by the blueprint
└── test/                          # Test suite (see below)
setup.py                           # Package metadata and dependencies
tox.ini                            # flake8 / black line-length config
.github/workflows/                 # CI (python-test.yml) and PyPI publish (python-publish.yml)
README.md                          # User-facing documentation
```

### Key concepts

- **`Parameter` subclasses** (`Route`, `Query`, `Json`, `Form`, `File`, `MultiSource`) define
  *where* an input comes from. Each may override conversion behaviour but shares validation
  logic from the base `Parameter` in `parameter_types/parameter.py`.
- **`ValidateParameters`** wraps a view: it reads the signature, pulls each declared input from
  the appropriate source, runs type checking + constraints, and calls the view with validated
  values. It also records function metadata used to generate documentation.
- **`docs_blueprint`** turns the recorded metadata + route docstrings into OpenAPI and the
  legacy JSON/HTML formats.

## Setup

Develop against a virtual environment (do not install into a global/base interpreter):

```sh
python -m venv .venv
source .venv/bin/activate
pip install pytest
pip install -r flask_parameter_validation/test/requirements.txt
```

`flask_parameter_validation/test/requirements.txt` installs the local package (via `../../`),
`Flask`, `requests`, and `pytest`, so the editable package is available to the tests.

## Testing

The test suite uses **pytest** and Flask's test client. There is no network or database
dependency — tests spin up an in-process Flask app (`test/testing_application.py`) whose routes
come from the blueprints in `test/testing_blueprints/`.

Run the full suite from inside the package directory (this matches CI):

```sh
cd flask_parameter_validation
pytest
```

Useful variants:

```sh
pytest test/test_json_params.py          # one source's tests
pytest -k uuid                           # tests matching an expression
pytest -q                                # quieter output
```

### Test layout

- `test/conftest.py` — `app`, `client`, and `runner` fixtures.
- `test/testing_application.py` — `create_app()`; registers per-type and multi-source blueprints
  and the docs blueprint. OpenAPI is enabled here.
- `test/test_*.py` — one module per input source (`json`, `query`, `form`, `route`, `file`,
  `multi_source`) plus `test_api_docs.py` for documentation generation.
- `test/testing_blueprints/` — routes exercising each type/source combination.

### Adding or changing behaviour

- New behaviour needs tests. Match the existing pattern: add/extend a blueprint in
  `testing_blueprints/` to expose a route, then assert against it via the `client` fixture in
  the matching `test_*.py`.
- Changes that affect generated documentation must keep `test_api_docs.py` passing.
- The library targets Python 3.9+. Avoid syntax/APIs newer than 3.9 (e.g. be careful with
  `typing` constructs, `is_typeddict`, and `Annotated` differences — there is version-specific
  handling already in the codebase). CI runs the matrix 3.9 → 3.13, so verify across versions
  when touching type introspection.

## Code style

- `tox.ini` sets flake8 `max-line-length = 120` (with `E501` ignored) and black
  `line-length = 119`. There is no enforced formatter in CI; keep lines within these bounds and
  match the surrounding style.
- Follow the existing structure: one input source per module under `parameter_types/`, shared
  logic on the base `Parameter`.
- Raise the project's own exceptions (`exceptions/exceptions.py`) for validation/configuration
  errors rather than generic ones.

## Pull requests & commits

- CI (`.github/workflows/python-test.yml`) runs pytest on every push and PR to `master` across
  Python 3.9–3.13; all versions must pass.
- Keep commit messages short and imperative, matching the existing history
  (e.g. "Add test for …", "Fix incorrect regex").
- Bump `version` in `setup.py` for releases; publishing is handled by
  `.github/workflows/python-publish.yml`.
- The README is the package's PyPI long description — update it when public behaviour changes.

## Notes for agents

- Do not commit unless explicitly asked.
  treat it as dead code or delete it without confirmation.
- This environment's base interpreter does not have the dependencies installed; create a
  virtualenv (above) before running tests.
