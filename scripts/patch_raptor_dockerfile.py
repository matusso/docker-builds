#!/usr/bin/env python3
"""Apply the CI-only patches RAPTOR's devcontainer Dockerfile needs.

RAPTOR is tracked from upstream ``main`` and its ``.devcontainer/Dockerfile`` is
written for a single-architecture devcontainer, not for a multi-arch registry
build. Rather than fork it, the small set of deltas below is applied in CI.

Every patch is declared with an explicit ``required`` flag:

* ``required=True``  — the patch fixes something that breaks the CI build. If the
  target text is gone, upstream changed materially and the build stops so the
  patch can be reviewed.
* ``required=False`` — the patch works around an upstream problem that upstream
  may fix on its own. A missing target is reported and skipped, because the
  build succeeds without it.

That distinction matters: an earlier revision of this patcher hard-failed on
every patch, so the whole workflow broke the moment upstream fixed two of the
issues it was working around.

Usage::

    python3 scripts/patch_raptor_dockerfile.py raptor/.devcontainer/Dockerfile
    python3 scripts/patch_raptor_dockerfile.py --check raptor/.devcontainer/Dockerfile
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

# --- patch definitions -----------------------------------------------------

CODEQL_FIND = """\
ARG CODEQL_VERSION=2.15.5
RUN mkdir -p /opt/codeql \\
    && curl -L "https://github.com/github/codeql-cli-binaries/releases/download/v${CODEQL_VERSION}/codeql-linux64.zip" -o /tmp/codeql.zip \\
    && unzip /tmp/codeql.zip -d /opt \\
    && rm /tmp/codeql.zip \\
    && ln -s /opt/codeql/codeql /usr/local/bin/codeql"""

CODEQL_REPLACE = """\
ARG CODEQL_VERSION=2.15.5
ARG TARGETARCH
RUN mkdir -p /opt/codeql \\
    && if [ "$TARGETARCH" = "amd64" ]; then \\
         curl -L "https://github.com/github/codeql-cli-binaries/releases/download/v${CODEQL_VERSION}/codeql-linux64.zip" -o /tmp/codeql.zip \\
         && unzip /tmp/codeql.zip -d /opt \\
         && rm /tmp/codeql.zip \\
         && ln -s /opt/codeql/codeql /usr/local/bin/codeql; \\
       else \\
         printf '#!/bin/sh\\necho "CodeQL CLI is not bundled on %s; upstream releases only publish linux64 binaries." >&2\\nexit 1\\n' "$TARGETARCH" > /usr/local/bin/codeql \\
         && chmod +x /usr/local/bin/codeql; \\
       fi"""


@dataclass(frozen=True)
class Patch:
    """A single literal find/replace against the Dockerfile."""

    name: str
    find: str
    replace: str
    required: bool
    why: str


PATCHES: tuple[Patch, ...] = (
    Patch(
        name="codeql-arch-guard",
        find=CODEQL_FIND,
        replace=CODEQL_REPLACE,
        required=True,
        why=(
            "GitHub publishes the CodeQL CLI as linux64 only, so the unguarded "
            "download fails the arm64 leg of the build. Non-amd64 images get a "
            "stub that exits with an explanatory message instead."
        ),
    ),
    Patch(
        name="devcontainer-base-tag",
        find="FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm",
        replace="FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm",
        required=False,
        why=(
            "The ':1-' variant prefix has not always resolved for every "
            "architecture in the manifest list; the unprefixed tag does."
        ),
    ),
)


# --- driver ----------------------------------------------------------------


def summarise(lines: list[str]) -> None:
    """Append a report to the job summary when running under GitHub Actions."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    with open(summary_path, "a", encoding="utf-8") as handle:
        handle.write("### RAPTOR Dockerfile patches\n\n")
        handle.writelines(f"{line}\n" for line in lines)
        handle.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dockerfile", type=Path, help="Path to the Dockerfile to patch.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Report which patches would apply without writing any changes.",
    )
    args = parser.parse_args(argv)

    path: Path = args.dockerfile
    if not path.is_file():
        print(f"error: {path} does not exist", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    report: list[str] = []
    applied = 0
    missing_required: list[Patch] = []

    for patch in PATCHES:
        already = patch.replace in text
        found = patch.find in text

        if already and not found:
            report.append(f"- `{patch.name}`: already applied")
            continue

        if found:
            text = text.replace(patch.find, patch.replace, 1)
            applied += 1
            report.append(f"- `{patch.name}`: applied")
            continue

        if patch.required:
            missing_required.append(patch)
            report.append(f"- `{patch.name}`: **target text not found (required)**")
        else:
            report.append(f"- `{patch.name}`: skipped, target text not found (optional)")
            print(
                f"notice: optional patch '{patch.name}' no longer applies; "
                f"upstream may have fixed it. Reason it existed: {patch.why}",
                file=sys.stderr,
            )

    for line in report:
        print(line.replace("**", "").replace("`", ""))
    summarise(report)

    if missing_required:
        for patch in missing_required:
            print(
                f"::error::Required patch '{patch.name}' did not apply. Upstream "
                f"changed the text this patch targets. Why it exists: {patch.why}",
                file=sys.stderr,
            )
        return 1

    if args.check:
        print(f"check: {applied} patch(es) would be applied")
        return 0

    if applied:
        path.write_text(text, encoding="utf-8")
        print(f"wrote {path} ({applied} patch(es) applied)")
    else:
        print(f"{path} already up to date")

    return 0


if __name__ == "__main__":
    sys.exit(main())
