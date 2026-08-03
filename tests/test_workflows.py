"""Supply-chain and least-privilege conventions for every workflow.

The rules here encode failures this repository has actually had: an action on a
mutable ref, and workflows without a concurrency group or a timeout.
"""

from __future__ import annotations

import re
from pathlib import Path

import catalog
import pytest
from conftest import all_workflows, caller_workflows

ALL = all_workflows()
ALL_IDS = [path.name for path in ALL]
CALLERS = caller_workflows()
CALLER_IDS = [path.name for path in CALLERS]

#: Refs that move under us. Pinning to a tag is the minimum; these are worse.
MUTABLE_REFS = ("@master", "@main", "@HEAD")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def action_refs(text: str) -> list[str]:
    """External actions a workflow calls, excluding local reusable workflows."""
    return [ref for ref in re.findall(r"^\s+uses:\s*(\S+)", text, re.M) if not ref.startswith("./")]


def jobs_of(text: str) -> list[tuple[str, str]]:
    """Return ``[(job_name, job_body)]``, sharing the catalog reader's parser."""
    return sorted(catalog.job_blocks(text).items())


@pytest.mark.parametrize("path", ALL, ids=ALL_IDS)
def test_actions_are_not_on_mutable_refs(path: Path) -> None:
    for ref in action_refs(read(path)):
        for mutable in MUTABLE_REFS:
            assert not ref.endswith(mutable), (
                f"{path.name}: `{ref}` tracks a mutable ref. Pin it to a release tag "
                "so a compromised upstream cannot silently change our builds."
            )


@pytest.mark.parametrize("path", ALL, ids=ALL_IDS)
def test_actions_are_version_pinned(path: Path) -> None:
    for ref in action_refs(read(path)):
        assert "@" in ref, f"{path.name}: `{ref}` has no version"
        version = ref.split("@", 1)[1]
        assert re.match(r"^(v?\d|[0-9a-f]{40}$)", version), (
            f"{path.name}: `{ref}` is not pinned to a version tag or commit SHA"
        )


@pytest.mark.parametrize("path", ALL, ids=ALL_IDS)
def test_declares_explicit_permissions(path: Path) -> None:
    """Never rely on the repository's default token scope."""
    assert "permissions:" in read(path), (
        f"{path.name}: declares no `permissions:`, so it inherits the repository default."
    )


@pytest.mark.parametrize("path", ALL, ids=ALL_IDS)
def test_every_job_has_a_timeout(path: Path) -> None:
    """A hung build should fail, not occupy a runner for six hours."""
    jobs = jobs_of(read(path))
    assert jobs, f"{path.name}: no jobs parsed, so this check would be vacuous"

    for name, body in jobs:
        # Jobs delegating to a reusable workflow inherit its per-job timeouts.
        if "uses:" in body:
            continue
        assert "timeout-minutes:" in body, f"{path.name}: job `{name}` has no timeout-minutes"


@pytest.mark.parametrize("path", CALLERS, ids=CALLER_IDS)
def test_caller_has_a_concurrency_group(path: Path) -> None:
    """Two pushes in quick succession must not race to publish the same tag."""
    assert "concurrency:" in read(path), f"{path.name}: declares no concurrency group"


@pytest.mark.parametrize("path", CALLERS, ids=CALLER_IDS)
def test_caller_builds_on_pull_requests(path: Path) -> None:
    """Changes get a real two-architecture build before they reach main."""
    assert "pull_request:" in read(path), (
        f"{path.name}: has no pull_request trigger, so changes merge unverified."
    )


@pytest.mark.parametrize("path", CALLERS, ids=CALLER_IDS)
def test_caller_is_manually_dispatchable(path: Path) -> None:
    assert "workflow_dispatch:" in read(path), f"{path.name}: cannot be triggered manually"


@pytest.mark.parametrize("path", CALLERS, ids=CALLER_IDS)
def test_image_callers_do_not_push_from_pull_requests(path: Path) -> None:
    """A fork's pull request must never be able to publish."""
    text = read(path)
    if "_build-image.yml" not in text:
        pytest.skip(f"{path.name} does not publish an image")
    assert "push: ${{ github.event_name != 'pull_request' }}" in text, (
        f"{path.name}: must gate publishing on the event not being a pull request."
    )


def test_no_workflow_still_uses_the_retired_scanner() -> None:
    """Snyk and the unmaintained SARIF converter were replaced by Trivy."""
    for path in ALL:
        text = read(path).lower()
        assert "snyk" not in text, f"{path.name}: still references Snyk"
        assert "garethr" not in text, (
            f"{path.name}: still uses garethr/snyk-to-sarif, an unmaintained action."
        )


def test_reusable_build_workflow_uses_native_runners() -> None:
    """Cross-architecture builds run natively, never under QEMU emulation."""
    text = read(Path(".github/workflows/_build-image.yml").resolve())
    assert "ubuntu-24.04-arm" in text, "arm64 must build on a native arm runner"
    assert "setup-qemu-action" not in text, (
        "QEMU emulation was removed in favour of native runners; reintroducing it "
        "would make arm64 builds many times slower."
    )
