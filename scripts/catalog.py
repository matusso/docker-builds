#!/usr/bin/env python3
"""Read the repository's declared state, and say where it contradicts itself.

Which version of a tool we publish is recorded in three places:

* the ``version:`` input in ``.github/workflows/<tool>.yml``
* the ``upstream-ref:`` of that workflow's SonarCloud job, when it has one
* the catalog table in ``README.md``

A bump that misses one is silent: the image publishes fine and the documentation
quietly lies. This module is the single definition of what "consistent" means.
It is consumed by two entry points — ``scripts/check_catalog.py`` for a
zero-dependency local run, and ``tests/test_catalog.py`` for per-image reporting
under pytest.

Deliberately stdlib-only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"
FILES_DIR = REPO_ROOT / "files"
README = REPO_ROOT / "README.md"

#: Workflows that do not publish an image through the shared pipeline.
NON_IMAGE_WORKFLOWS = frozenset({"ci.yml", "caddy.yml"})

#: Images that track a branch rather than a release. The workflow's version is a
#: runtime expression, so the catalog documents the tag shape instead.
COMMIT_TRACKED = {"raptor": "sha-<commit>"}


class CatalogError(Exception):
    """The repository could not be parsed, which is itself a failure."""


@dataclass(frozen=True)
class Problem:
    """One contradiction, attributed to the image it concerns."""

    image: str
    message: str

    def __str__(self) -> str:
        return f"{self.image}: {self.message}"


@dataclass(frozen=True)
class ImageSpec:
    """What a caller workflow declares about the image it publishes."""

    image: str
    version: str
    workflow: str
    context: str
    upstream_repo: str | None
    sonar_ref: str | None
    platforms: str | None
    licenses: str | None
    has_smoke_command: bool

    @property
    def is_commit_tracked(self) -> bool:
        return self.image in COMMIT_TRACKED

    @property
    def is_local_dockerfile(self) -> bool:
        """True when we own the Dockerfile, rather than building upstream's."""
        return self.upstream_repo is None


def _scalar(text: str, key: str) -> str | None:
    """First ``key: value`` mapping in ``text``, ignoring keys with no value.

    Horizontal whitespace only — ``\\s`` would match a newline and happily read
    the *next* line's value for a key that has none of its own.
    """
    match = re.search(rf"^[ \t]+{re.escape(key)}:[ \t]*(\S.*?)[ \t]*$", text, re.M)
    if not match:
        return None
    return match.group(1).strip("\"'")


def job_blocks(text: str) -> dict[str, str]:
    """Return ``{job_name: job_body}`` for the workflow's ``jobs:`` mapping.

    Scoped to the ``jobs:`` block deliberately: matching two-space keys across
    the whole file also picks up ``push:`` and ``pull_request:`` from ``on:``.
    """
    if "\njobs:\n" not in text:
        return {}
    body = text.split("\njobs:\n", 1)[1]
    return dict(re.findall(r"^  ([a-z][a-z0-9_-]*):\n((?:(?:    |\t).*\n|\n)*)", body, re.M))


def _block_calling(text: str, reusable: str) -> str | None:
    """The body of the job that calls a given reusable workflow.

    Per-job scoping matters: a tool's sonar job legitimately declares its own
    ``upstream-repo``, and reading that as the image job's would misclassify a
    locally built image as an upstream build.
    """
    for body in job_blocks(text).values():
        if reusable in body:
            return body
    return None


@cache
def image_specs() -> dict[str, ImageSpec]:
    """Parse every caller workflow that publishes an image."""
    specs: dict[str, ImageSpec] = {}

    for path in sorted(WORKFLOW_DIR.glob("*.yml")):
        if path.name.startswith("_") or path.name in NON_IMAGE_WORKFLOWS:
            continue

        text = path.read_text(encoding="utf-8")
        build = _block_calling(text, "_build-image.yml")

        # A template change that defeats this parse must fail loudly rather than
        # silently reduce the checks to nothing.
        if build is None:
            raise CatalogError(
                f"{path.name}: no job calls _build-image.yml. If the caller "
                "template changed, update scripts/catalog.py."
            )

        image = _scalar(build, "image")
        version = _scalar(build, "version")
        if not image or not version:
            raise CatalogError(
                f"{path.name}: could not find both an `image:` and a `version:` "
                "input on the job that calls _build-image.yml."
            )

        sonar = _block_calling(text, "_sonar-scan.yml")

        specs[image] = ImageSpec(
            image=image,
            version=version,
            workflow=path.name,
            context=_scalar(build, "context") or "",
            upstream_repo=_scalar(build, "upstream-repo"),
            sonar_ref=_scalar(sonar, "upstream-ref") if sonar else None,
            platforms=_scalar(build, "platforms"),
            licenses=_scalar(build, "licenses"),
            has_smoke_command="smoke-command:" in build,
        )

    if not specs:
        raise CatalogError(f"No image workflows found in {WORKFLOW_DIR}.")
    return specs


@cache
def catalog_rows() -> dict[str, str]:
    """Parse ``{image: version}`` from the README catalog table."""
    rows = dict(
        re.findall(
            r"^\|\s*`([a-z0-9._-]+)`\s*\|\s*`([^`]+)`\s*\|",
            README.read_text(encoding="utf-8"),
            re.M,
        )
    )
    if not rows:
        raise CatalogError("Could not parse any rows from the README catalog table.")
    return rows


@cache
def badge_count() -> int | None:
    match = re.search(
        r"!\[images\]\(https://img\.shields\.io/badge/images-(\d+)-",
        README.read_text(encoding="utf-8"),
    )
    return int(match.group(1)) if match else None


@cache
def caddy_versions() -> tuple[str | None, str | None]:
    """Return the Caddy version as (pinned in workflow, documented in README)."""
    workflow = (WORKFLOW_DIR / "caddy.yml").read_text(encoding="utf-8")
    pinned = re.search(r'CADDY_VERSION:\s*"(\S+)"', workflow)
    documented = re.search(r"`(v\d+\.\d+\.\d+)` built with", README.read_text(encoding="utf-8"))
    return (
        pinned.group(1) if pinned else None,
        documented.group(1) if documented else None,
    )


def problems_for(image: str) -> list[Problem]:
    """Every contradiction concerning one image."""
    spec = image_specs()[image]
    rows = catalog_rows()
    found: list[Problem] = []

    expected = COMMIT_TRACKED.get(image, spec.version)
    documented = rows.get(image)

    if documented is None:
        found.append(
            Problem(image, f"pinned in {spec.workflow} but missing from the README catalog table.")
        )
    elif documented != expected:
        found.append(
            Problem(
                image,
                f"{spec.workflow} pins `{expected}` but the README catalog says `{documented}`.",
            )
        )

    # The SonarCloud job must analyse the version the image actually packages.
    if spec.sonar_ref and not spec.is_commit_tracked and spec.sonar_ref != spec.version:
        found.append(
            Problem(
                image,
                f"{spec.workflow} builds `{spec.version}` but its sonar job "
                f"analyses `{spec.sonar_ref}`.",
            )
        )

    return found


def collect_problems() -> list[Problem]:
    """Every contradiction in the repository."""
    specs = image_specs()
    rows = catalog_rows()
    found: list[Problem] = []

    for image in sorted(specs):
        found.extend(problems_for(image))

    for image in sorted(set(rows) - set(specs)):
        found.append(Problem(image, "listed in the README catalog but no workflow publishes it."))

    declared = badge_count()
    if declared is None:
        found.append(Problem("README", "could not find the image-count badge."))
    elif declared != len(rows):
        found.append(
            Problem(
                "README",
                f"badge claims {declared} images but the catalog table lists {len(rows)}.",
            )
        )

    pinned, documented = caddy_versions()
    if pinned is None:
        found.append(Problem("caddy", "caddy.yml has no CADDY_VERSION pin."))
    elif documented is None:
        found.append(Problem("caddy", "README has no Caddy version in the release section."))
    elif pinned != documented:
        found.append(
            Problem("caddy", f"caddy.yml pins `{pinned}` but the README says `{documented}`.")
        )

    return found
