"""The Dockerfiles we own follow one template.

"Align all packages to the same format" is only true for as long as something
checks it, so each convention in CONTRIBUTING.md is asserted here.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from conftest import local_dockerfiles

DOCKERFILES = local_dockerfiles()
IDS = [path.parent.name for path in DOCKERFILES]

#: Labels every image must carry, so a pulled image is self-describing.
REQUIRED_LABELS = (
    "org.opencontainers.image.title",
    "org.opencontainers.image.description",
    "org.opencontainers.image.version",
    "org.opencontainers.image.source",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def from_lines(text: str) -> list[str]:
    return re.findall(r"^FROM\s+(.+)$", text, re.M)


@pytest.mark.parametrize("path", DOCKERFILES, ids=IDS)
def test_starts_with_syntax_directive(path: Path) -> None:
    """BuildKit only honours the syntax directive on the very first line."""
    first = read(path).splitlines()[0]
    assert first == "# syntax=docker/dockerfile:1", (
        f"{path} must open with the BuildKit syntax directive, found: {first!r}"
    )


@pytest.mark.parametrize("path", DOCKERFILES, ids=IDS)
def test_documents_upstream(path: Path) -> None:
    """The header explains what this is and where it came from."""
    header = "\n".join(read(path).splitlines()[:14])
    assert "Upstream: https://github.com/" in header, (
        f"{path} header must link the upstream project."
    )


@pytest.mark.parametrize("path", DOCKERFILES, ids=IDS)
def test_base_images_are_pinned(path: Path) -> None:
    """No floating tags, and no ARG indirection that would blind Dependabot."""
    for image in from_lines(read(path)):
        ref = image.split(" AS ")[0].strip()
        assert ":" in ref, f"{path}: `FROM {ref}` has no tag"
        assert not ref.endswith(":latest"), f"{path}: `FROM {ref}` uses a floating tag"
        assert "${" not in ref, (
            f"{path}: `FROM {ref}` builds its tag from an ARG. Dependabot cannot "
            "resolve ARG interpolation in a FROM line and will silently stop "
            "updating this image; pin the tag literally."
        )
        assert re.search(r":\d", ref), f"{path}: `FROM {ref}` is not pinned to a version"


@pytest.mark.parametrize("path", DOCKERFILES, ids=IDS)
def test_is_multi_stage_with_a_runtime_stage(path: Path) -> None:
    """Build toolchains and git must not reach the published image."""
    stages = re.findall(r"^FROM\s+\S+\s+AS\s+(\S+)$", read(path), re.M)
    assert len(stages) >= 2, f"{path}: expected a build/fetch stage and a runtime stage"
    assert stages[-1] == "runtime", f"{path}: the final stage should be named `runtime`"


@pytest.mark.parametrize("path", DOCKERFILES, ids=IDS)
def test_runtime_stage_has_no_build_toolchain(path: Path) -> None:
    """git and compilers belong to the build stage only."""
    text = read(path)
    runtime = text[text.rindex("FROM ") :]
    for forbidden in ("build-base", "cargo", " git\n", "python3-dev"):
        assert forbidden not in runtime, (
            f"{path}: runtime stage installs `{forbidden.strip()}`; keep it in the build stage."
        )


@pytest.mark.parametrize("path", DOCKERFILES, ids=IDS)
def test_declares_required_oci_labels(path: Path) -> None:
    text = read(path)
    for label in REQUIRED_LABELS:
        assert label in text, f"{path}: missing `{label}`"


@pytest.mark.parametrize("path", DOCKERFILES, ids=IDS)
def test_accepts_release_version_with_a_default(path: Path) -> None:
    """The pipeline passes RELEASE_VERSION; the default keeps standalone builds working."""
    assert re.search(r"^ARG RELEASE_VERSION=\S+", read(path), re.M), (
        f"{path}: needs `ARG RELEASE_VERSION=<default>` so it builds without --build-arg."
    )


@pytest.mark.parametrize("path", DOCKERFILES, ids=IDS)
def test_runs_as_non_root(path: Path) -> None:
    users = re.findall(r"^USER\s+(\S+)", read(path), re.M)
    assert users, f"{path}: declares no USER, so it would run as root"
    assert users[-1] == "10001:10001", (
        f"{path}: final USER is {users[-1]!r}; the convention is the numeric "
        "`10001:10001` so the uid is unambiguous to Kubernetes and Trivy."
    )


@pytest.mark.parametrize("path", DOCKERFILES, ids=IDS)
def test_apk_uses_no_cache(path: Path) -> None:
    """`--no-cache` replaces the apk update/add pair and leaves no index behind."""
    for line in read(path).splitlines():
        if "apk add" in line:
            assert "--no-cache" in line, f"{path}: `{line.strip()}` is missing --no-cache"
    assert "apk update" not in read(path), (
        f"{path}: `apk update` is redundant alongside `apk add --no-cache`"
    )


@pytest.mark.parametrize("path", DOCKERFILES, ids=IDS)
def test_declares_an_entrypoint_or_command(path: Path) -> None:
    text = read(path)
    assert re.search(r"^(ENTRYPOINT|CMD)\s", text, re.M), (
        f"{path}: declares neither ENTRYPOINT nor CMD"
    )


def test_pocketbase_defines_a_healthcheck() -> None:
    """The one long-running service should report its own readiness."""
    text = read(Path("files/pocketbase/Dockerfile").resolve())
    assert "HEALTHCHECK" in text
    # Exec form avoids depending on a shell inside the healthcheck.
    assert re.search(r"CMD\s*\[", text[text.index("HEALTHCHECK") :])


def test_pocketbase_verifies_its_download() -> None:
    """A binary fetched over the network must be checksummed before use."""
    text = read(Path("files/pocketbase/Dockerfile").resolve())
    assert "checksums.txt" in text and "sha256sum -c" in text, (
        "pocketbase downloads a release archive; it must verify it against the "
        "publisher's checksum file."
    )
