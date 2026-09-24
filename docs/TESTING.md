# Testing & Coverage Guide for APEX Skills

## Overview

APEX Skills includes comprehensive unit tests for the export processing utilities and infrastructure to support future integration tests.

## Running Tests

### Prerequisites

Ensure test dependencies are installed:

```bash
pip install -e . -r requirements.txt
# or specifically:
pip install pytest pytest-cov
```

### Run All Tests

```bash
pytest
```

### Run Specific Test Class or Function

```bash
# Run all tests in a test class
pytest tests/test_apex_export_utilities.py::TestGetYamlField

# Run a specific test
pytest tests/test_apex_export_utilities.py::TestGetYamlField::test_simple_field_extraction
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Only Unit Tests

```bash
pytest -m unit
```

### Run Only Integration Tests (requires Oracle connection)

```bash
pytest -m integration
```

## Coverage Reports

### Generate Coverage Report (Terminal)

```bash
pytest --cov=scripts --cov-report=term-missing
```

Output shows:
- Lines executed
- Lines not covered (`>>>`marks)
- Coverage percentage per file

### Generate HTML Coverage Report

```bash
pytest --cov=scripts --cov-report=html
```

Then open `htmlcov/index.html` in your browser to see detailed coverage visualization.

### Generate XML Coverage Report (CI/CD)

```bash
pytest --cov=scripts --cov-report=xml
```

## Configuration Files

### `pytest.ini`

Configures pytest behavior:
- Test discovery patterns
- Test paths (`tests/`)
- Markers (unit, integration, slow, requires_oracle)
- Output formatting

### `.coveragerc`

Configures coverage measurement:
- Source paths to measure (`scripts/`, `skills/*/scripts/`)
- Lines to exclude from coverage (pragma comments, abstract methods, etc.)
- Report formats (terminal, HTML, XML)

## Test Organization

Tests are located in the `tests/` directory with the following structure:

```
tests/
├── __init__.py                           # Test package marker
├── test_apex_export_utilities.py         # Tests for export processing
└── test_*.py                             # Additional test files (pattern: test_*.py)
```

## Test Markers

Tests use pytest markers for classification:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Tests requiring external resources
- `@pytest.mark.slow` - Slow running tests (excluded from quick runs)
- `@pytest.mark.requires_oracle` - Tests requiring Oracle APEX connection

Example usage:

```bash
pytest -m unit              # Run only unit tests
pytest -m "not requires_oracle"  # Skip Oracle-dependent tests
```

## Current Test Coverage

### Covered Modules

- ✅ `scripts/apex_export_utilities.py` - Core export processing functions
  - `get_yaml_field()`: Unified YAML field parsing
  - `extract_apex_export_metadata()`: ZIP metadata extraction
  - `list_export_pages()`: Page enumeration from exports

### Not Yet Covered

- 🚧 `scripts/manage_apex_credentials.py` - Credential management (requires keyring)
- 🚧 `skills/*/scripts/validate_export.py` - Export validation CLI
- 🚧 `skills/*/scripts/inspect_export.py` - Export inspection CLI
- 🚧 `skills/*/scripts/mine_export_patterns.py` - Pattern mining CLI

## Adding New Tests

### Test File Template

```python
"""Unit tests for module_name."""

import pytest

class TestFeature:
    """Tests for specific feature."""

    @pytest.mark.unit
    def test_happy_path(self):
        """Describe what this test verifies."""
        # Arrange
        input_data = ...

        # Act
        result = function_under_test(input_data)

        # Assert
        assert result == expected
```

### Running Before Commit

Before committing, run tests to ensure quality:

```bash
# Quick unit tests
pytest -m unit

# Full coverage
pytest --cov=scripts --cov-report=term-missing
```

## CI/CD Integration

The `.pre-commit-config.yaml` hook includes pytest in pre-commit checks. To enable:

```bash
pre-commit install
```

This will automatically run tests on commit (can be bypassed with `--no-verify` if needed).

## Troubleshooting

### Tests Not Found

Ensure test files follow the pattern `test_*.py` and are in the `tests/` directory.

```bash
pytest --collect-only  # List discovered tests
```

### Import Errors

Tests add `scripts/` to the Python path. If imports still fail:

```bash
export PYTHONPATH=/home/user/apex.skills/scripts:$PYTHONPATH
```

### Coverage Not Generated

Ensure `pytest-cov` is installed:

```bash
pip install pytest-cov
```

## Future Improvements

1. **Integration Tests**: Add tests for Oracle APEX connections
2. **Mocking**: Mock external dependencies (keyring, oracledb)
3. **Fixtures**: Create reusable test data (sample exports, credentials)
4. **CI/CD**: Integrate coverage reports into GitHub Actions
5. **CLI Tests**: Test command-line scripts with click or typer

## References

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [coverage.py documentation](https://coverage.readthedocs.io/)

---

**Last Updated**: 2026-09-01

## Auditoría Windows

El umbral único de cobertura es 55%, definido en `.coveragerc`. La medición
observada el 2026-09-24 fue 60.65% de líneas, 43.12% de ramas y 56.63%
combinado con 485 pruebas aprobadas. El 80% es una meta gradual, no el umbral actual. Consulta
[`CI-LOCAL.md`](CI-LOCAL.md) para ejecutar localmente los controles de GitHub
Actions y entender cómo se interpreta la cobertura.

En Windows, `flake8` debe ejecutarse con `--jobs=1` cuando el entorno impide
crear procesos auxiliares. `detect-secrets` debe excluir los artefactos locales
(`.venv`, `.upstreams`, `.pytest_cache`, `htmlcov` y similares), tal como hace
el control de seguridad del repositorio.
