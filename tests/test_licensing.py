"""The repository's own licence, and the licences it attributes to each image.

Two distinct claims are checked. First, that this repository carries the licence
it says it does. Second, and more importantly, that every published image
declares the upstream licence it actually ships — an image whose
``org.opencontainers.image.licenses`` label is missing or wrong is a compliance
problem for whoever redistributes it, and two of these images are copyleft.
"""

from __future__ import annotations

import re
from pathlib import Path

import catalog
import pytest
from conftest import local_dockerfiles

REPO_ROOT = catalog.REPO_ROOT
LICENSE = REPO_ROOT / "LICENSE"
README = REPO_ROOT / "README.md"

DECLARED_LICENCE = "Apache-2.0"

#: Images whose upstream licence obliges anyone redistributing them. The README
#: must keep saying so; silently dropping the warning is the failure to prevent.
COPYLEFT = {
    "kiterunner": "AGPL-3.0",
    "dirsearch": "GPL-2.0",
}

IMAGES = sorted(catalog.image_specs())


def license_text() -> str:
    return LICENSE.read_text(encoding="utf-8")


def readme_text() -> str:
    return README.read_text(encoding="utf-8")


def licensing_section() -> str:
    text = readme_text()
    start = text.index("## Licensing")
    return text[start:]


# --- this repository's own licence ------------------------------------------


def test_license_file_exists() -> None:
    assert LICENSE.is_file(), "the repository has no LICENSE file"


def test_license_is_apache_2_0() -> None:
    text = license_text()
    assert "Apache License" in text
    assert "Version 2.0, January 2004" in text
    assert "TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION" in text


def test_license_retains_the_clauses_that_motivated_the_choice() -> None:
    """The patent, contribution and trademark clauses are why Apache-2.0."""
    text = license_text()
    assert "3. Grant of Patent License" in text
    assert "5. Submission of Contributions" in text
    assert "6. Trademarks" in text


def test_license_names_a_copyright_holder() -> None:
    """An unfilled placeholder is worse than no notice — it looks deliberate."""
    text = license_text()
    assert "[yyyy]" not in text, "the appendix year placeholder was left unfilled"
    assert "[name of copyright owner]" not in text, (
        "the appendix copyright-owner placeholder was left unfilled"
    )
    assert re.search(r"^\s*Copyright \d{4}(-\d{4})? \S", text, re.M), (
        "no `Copyright <year> <holder>` notice found in the appendix"
    )


def test_readme_badge_matches_the_license_file() -> None:
    # Shields' path is `license-<label>-<colour>`; the label itself contains
    # hyphens, escaped as '--', so match greedily up to the final colour segment.
    badge = re.search(
        r"!\[license\]\(https://img\.shields\.io/badge/license-(.+)-[a-z]+\)", readme_text()
    )
    assert badge, "README has no license badge"
    assert badge.group(1).replace("--", "-") == DECLARED_LICENCE


def test_readme_links_the_license_file() -> None:
    assert "(LICENSE)" in readme_text(), "README should link to the LICENSE file"


# --- the licences we attribute to each published image ----------------------


@pytest.mark.parametrize("image", IMAGES)
def test_every_image_declares_a_licence(image: str) -> None:
    """The pipeline stamps this onto the image as an OCI label."""
    spec = catalog.image_specs()[image]
    assert spec.licenses, (
        f"{spec.workflow} declares no `licenses:` input, so {image} would publish "
        "without an org.opencontainers.image.licenses label."
    )


@pytest.mark.parametrize("image", IMAGES)
def test_declared_licence_is_a_recognisable_identifier(image: str) -> None:
    """Either a plausible SPDX expression, or an explicit LicenseRef.

    MVT ships a bespoke, non-OSI licence; claiming a real SPDX id for it would be
    wrong, so `LicenseRef-` is the correct way to say "not a standard licence".
    """
    declared = catalog.image_specs()[image].licenses
    assert declared
    assert re.fullmatch(r"(LicenseRef-[\w.-]+|[A-Za-z0-9.+-]+)", declared), (
        f"{image}: `{declared}` is not a usable licence identifier"
    )


@pytest.mark.parametrize("image", IMAGES)
def test_image_licence_appears_in_the_readme(image: str) -> None:
    assert f"`{image}`" in licensing_section(), (
        f"{image} is published but absent from the README licensing table, so "
        "nobody redistributing it can tell what terms apply."
    )


@pytest.mark.parametrize("image", sorted(COPYLEFT))
def test_copyleft_images_are_flagged_in_the_readme(image: str) -> None:
    """Dropping this warning would quietly create a compliance trap."""
    section = licensing_section()
    assert COPYLEFT[image] in section, (
        f"{image} ships {COPYLEFT[image]} code; the README licensing section must keep saying so."
    )


@pytest.mark.parametrize("image", sorted(COPYLEFT))
def test_copyleft_declaration_matches_upstream(image: str) -> None:
    declared = catalog.image_specs()[image].licenses
    assert declared and declared.startswith(COPYLEFT[image]), (
        f"{image} declares `{declared}` but ships {COPYLEFT[image]} code"
    )


@pytest.mark.parametrize(
    "path", local_dockerfiles(), ids=[p.parent.name for p in local_dockerfiles()]
)
def test_dockerfile_licence_label_matches_the_workflow(path: Path) -> None:
    """The workflow's --label wins at build time; they must not disagree."""
    image = path.parent.name
    spec = catalog.image_specs().get(image)
    assert spec, f"no workflow publishes files/{image}"

    label = re.search(
        r'org\.opencontainers\.image\.licenses="([^"]+)"', path.read_text(encoding="utf-8")
    )
    assert label, f"{path} declares no org.opencontainers.image.licenses label"
    assert label.group(1) == spec.licenses, (
        f"{image}: Dockerfile says `{label.group(1)}` but {spec.workflow} passes "
        f"`{spec.licenses}`. The workflow label overrides the Dockerfile, so this "
        "silently publishes the workflow's value."
    )


def test_readme_separates_repo_licence_from_image_licences() -> None:
    """The distinction people get wrong, so it must stay explicit."""
    section = licensing_section()
    assert "This repository" in section
    assert "published images" in section
