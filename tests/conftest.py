"""Shared fixtures and path setup for the repository test suite.

These tests assert on the repository's declared state — Dockerfiles, workflows
and the README — rather than on running containers. Container behaviour is
covered by the per-architecture smoke tests in the build pipeline.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent

# scripts/ holds the catalog reader the suite shares with scripts/check_catalog.py.
sys.path.insert(0, str(REPO_ROOT / "scripts"))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


def local_dockerfiles() -> list[Path]:
    """Dockerfiles this repository owns, in a stable order."""
    return sorted((REPO_ROOT / "files").glob("*/Dockerfile"))


def caller_workflows() -> list[Path]:
    """Per-tool workflows, excluding reusable workflows and repo CI."""
    return sorted(
        path
        for path in (REPO_ROOT / ".github" / "workflows").glob("*.yml")
        if not path.name.startswith("_") and path.name != "ci.yml"
    )


def all_workflows() -> list[Path]:
    return sorted((REPO_ROOT / ".github" / "workflows").glob("*.yml"))
