# Developing `trash-cli`

Reference material for working on the code: environment setup, how
to run the tests, and the project's testing/coding conventions. For
the rules and expectations around submitting a PR, see
`CONTRIBUTING.md` instead.

## Development Environment Setup

- Clone the repository and create a virtual environment:

  ```
  git clone git@github.com:andreafrancia/trash-cli.git
  # or, over HTTPS: git clone https://github.com/andreafrancia/trash-cli.git
  cd trash-cli
  python -m venv .venv
  source .venv/bin/activate
  ```
- Install the project in editable mode, with its dev dependencies:

  ```
  pip install -e '.[dev]'
  ```

## Running the Test Suite

- For a quick run while developing:

  ```
  python -m pytest
  ```
- Some tests are marked as slow; you can select or skip them:

  ```
  pytest -m 'not slow'        # run only fast tests
  pytest -m 'slow'            # run slow tests
  pytest                      # run all tests
  ```
- Before submitting a PR, run the full check used by this project:

  ```
  scripts/pre-push
  ```
  This runs the tests (via `tox`), a sdist smoke test, and the type
  checks, for both Python 3 and Python 2.7 — the whole range this
  project supports.

  It needs a Python 3.10 interpreter (used by `tox`) and a Python 2.7
  interpreter on your machine: install 2.7 with
  [pyenv](https://github.com/pyenv/pyenv) (`pyenv install 2.7.18`), or
  point `PYTHON27` at an existing `python2.7` binary.

  The check can replace the project's editable install with a regular
  one. If later edits to `trashcli` stop showing up when you run its
  commands, reinstall it in editable mode:

  ```
  pip install -e '.[dev]'
  ```

## Configured Mocks vs Hand-Written Fakes and Stubs

- Hand-written fakes and stubs are generally preferred over configured
  mocks, because it's easier to build a simple interface that lets the
  reader understand what's happening, without having to understand the
  mocking library's quirks.

## Tests Framework

- The project started using `unittest` and then switched to `pytest`. Not all
  the tests have been migrated yet. For the new code please use `pytest`.
- PRs that just convert `unittest` tests to `pytest` tests are welcome; please
  change one test file per commit.
- Prefer using test classes in `pytest` tests too (see below) instead of
  test functions.
- Try to keep one test case (test class) for each test file.
- Try to keep the test case name in sync with the test file name; and use the
  convention of using `CamelCase` for the class and `snake_case` for the test
  filename. Example: in `test_put.py` the test case class is `TestPut`.

## Test Suggestions

- Please use `pytest.mark.parametrize` to avoid writing the same test multiple
  times.
- Please use `pytest.fixture` to avoid writing the same fixture multiple times.
- Please use `pytest.raises` instead of `unittest.assertRaises`.

## Testing Multiple Cases

- Try to split different test cases into different test files, different test
  classes, and different test methods: a single test method that tries to
  verify multiple behaviors may become hard to understand because the
  fixture might contain different elements.

## Testing Styles

Unittest test style:

```python
import unittest
class TestPut(unittest.TestCase):
    def setUp(self):
        self.fs = FakeFs()
        self.put_cmd = TrashPutCmd(self.fs)
    
    def test_put(self):
        self.fs.add_file('/path/to/file')
        self.put_cmd.run(['/path/to/file'])
        
        assert self.fs.path_exists('/path/to/file') is False
    
    def tearDown(self):
        self.fs.remove_all()
```

`pytest` style:
```python
class TestPut:
    def setup_method(self):
        self.fs = FakeFs()
        self.put_cmd = TrashPutCmd(self.fs)
    
    def test_put(self):
        self.fs.add_file('/path/to/file')
        self.put_cmd.run(['/path/to/file'])
        
        assert self.fs.path_exists('/path/to/file') is False
    
    def teardown_method(self):
        self.fs.remove_all()
```

`pytest` with fixtures style:
```python
@pytest.fixture
def fs():
    fs = RealFs()
    yield fs
    fs.remove_all()
    
@pytest.fixture
def put_cmd(fs):
    return TrashPutCmd(fs)

class TestPut:
    def test_put(self, fs, put_cmd):
        fs.add_file('/path/to/file')
        put_cmd.run(['/path/to/file'])
        
        assert fs.path_exists('/path/to/file') is False
```

## Coding Style / Type Checking

- This project doesn't currently enforce a linter or auto-formatter.
- It does enforce static type checking with `mypy`, for both Python 3
  and Python 2.7 (`scripts/check-types` and `scripts/py27/check-types`,
  both run by `scripts/pre-push`).
- We try to make code keep working on every Python version from 2.7
  through 3.14, so avoid syntax or stdlib features that aren't
  available across that whole range (e.g. no f-strings, no `match`
  statements).
