"""Smoke tests: the package imports and exposes the expected surface."""
from __future__ import annotations


def test_package_imports() -> None:
    """The top-level package imports and exposes a version string."""
    import emerald_ai

    assert isinstance(emerald_ai.__version__, str)
    assert emerald_ai.__version__.count(".") >= 1


def test_subpackages_import() -> None:
    """Each pipeline-stage subpackage imports without error."""
    import importlib

    for sub in (
        "emerald_ai.data",
        "emerald_ai.features",
        "emerald_ai.models",
        "emerald_ai.training",
        "emerald_ai.calibration",
        "emerald_ai.explain",
        "emerald_ai.fairness",
        "emerald_ai.eval",
    ):
        importlib.import_module(sub)


def test_config_paths_resolve() -> None:
    """The canonical paths object resolves and points inside the repo."""
    from emerald_ai.config import PATHS

    assert PATHS.root.exists()
    assert PATHS.literature.exists()


def test_cli_help_does_not_crash() -> None:
    """The CLI app object can be constructed and lists its commands."""
    from emerald_ai.cli import app

    assert app.info.name == "emerald"
