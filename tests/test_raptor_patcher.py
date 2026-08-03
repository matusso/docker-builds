"""Behavioural tests for the RAPTOR Dockerfile patcher.

The patcher is the component that broke: its predecessor hard-failed on every
patch, so the moment upstream fixed two of the problems it worked around, the
whole workflow started failing at the patch step. The distinction between a
required and an optional patch is therefore the behaviour worth pinning down.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import patch_raptor_dockerfile as patcher
import pytest

#: A minimal stand-in for upstream's Dockerfile, carrying both patch targets.
UPSTREAM = textwrap.dedent("""\
    FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm

    RUN apt-get update && apt-get install -y --no-install-recommends curl unzip

    ARG CODEQL_VERSION=2.15.5
    RUN mkdir -p /opt/codeql \\
        && curl -L "https://github.com/github/codeql-cli-binaries/releases/download/v${CODEQL_VERSION}/codeql-linux64.zip" -o /tmp/codeql.zip \\
        && unzip /tmp/codeql.zip -d /opt \\
        && rm /tmp/codeql.zip \\
        && ln -s /opt/codeql/codeql /usr/local/bin/codeql

    USER vscode
    """)


@pytest.fixture
def dockerfile(tmp_path: Path) -> Path:
    path = tmp_path / "Dockerfile"
    path.write_text(UPSTREAM, encoding="utf-8")
    return path


def test_applies_every_patch_to_pristine_upstream(dockerfile: Path) -> None:
    assert patcher.main([str(dockerfile)]) == 0

    patched = dockerfile.read_text(encoding="utf-8")
    # The CodeQL download is now guarded by architecture.
    assert "ARG TARGETARCH" in patched
    assert 'if [ "$TARGETARCH" = "amd64" ]' in patched
    # And the base image tag lost its variant prefix.
    assert "FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm" in patched


def test_is_idempotent(dockerfile: Path) -> None:
    """A rerun must not double-apply or start failing."""
    assert patcher.main([str(dockerfile)]) == 0
    once = dockerfile.read_text(encoding="utf-8")

    assert patcher.main([str(dockerfile)]) == 0
    assert dockerfile.read_text(encoding="utf-8") == once


def test_arm64_gets_a_codeql_stub_that_explains_itself(dockerfile: Path) -> None:
    """Non-amd64 builds must fail informatively, not mysteriously."""
    patcher.main([str(dockerfile)])
    patched = dockerfile.read_text(encoding="utf-8")

    assert "only publish linux64 binaries" in patched
    assert "chmod +x /usr/local/bin/codeql" in patched


def test_optional_patch_missing_is_tolerated(dockerfile: Path) -> None:
    """This is the regression: upstream fixing something must not break us.

    The base-image patch is optional. If upstream changes that line themselves,
    the build should carry on rather than hard-fail the way it used to.
    """
    text = dockerfile.read_text(encoding="utf-8").replace(
        "FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm",
        "FROM mcr.microsoft.com/devcontainers/python:3.13-trixie",
    )
    dockerfile.write_text(text, encoding="utf-8")

    assert patcher.main([str(dockerfile)]) == 0
    # Upstream's own choice is left alone.
    assert "python:3.13-trixie" in dockerfile.read_text(encoding="utf-8")


def test_required_patch_missing_fails_loudly(dockerfile: Path) -> None:
    """If the CodeQL block disappears, arm64 correctness is no longer assured."""
    text = dockerfile.read_text(encoding="utf-8").replace(patcher.CODEQL_FIND, "RUN echo rewritten")
    dockerfile.write_text(text, encoding="utf-8")

    assert patcher.main([str(dockerfile)]) == 1


def test_missing_file_is_an_error(tmp_path: Path) -> None:
    assert patcher.main([str(tmp_path / "absent")]) == 2


def test_check_mode_reports_without_writing(dockerfile: Path) -> None:
    before = dockerfile.read_text(encoding="utf-8")

    assert patcher.main(["--check", str(dockerfile)]) == 0
    assert dockerfile.read_text(encoding="utf-8") == before


def test_check_mode_still_fails_on_a_missing_required_patch(dockerfile: Path) -> None:
    text = dockerfile.read_text(encoding="utf-8").replace(patcher.CODEQL_FIND, "RUN echo rewritten")
    dockerfile.write_text(text, encoding="utf-8")

    assert patcher.main(["--check", str(dockerfile)]) == 1


def test_every_patch_documents_why_it_exists() -> None:
    """A patch nobody can justify is a patch nobody can safely remove."""
    for patch in patcher.PATCHES:
        assert patch.why.strip(), f"patch `{patch.name}` has no rationale"
        assert len(patch.why) > 40, f"patch `{patch.name}` rationale is too thin to act on"


def test_replacement_differs_from_the_text_it_replaces() -> None:
    for patch in patcher.PATCHES:
        assert patch.find != patch.replace, f"patch `{patch.name}` is a no-op"


def test_raptor_workflow_invokes_this_script() -> None:
    """The patcher is only useful if the pipeline actually runs it."""
    workflow = (Path(__file__).resolve().parent.parent / ".github/workflows/raptor.yml").read_text(
        encoding="utf-8"
    )
    assert "scripts/patch_raptor_dockerfile.py" in workflow
