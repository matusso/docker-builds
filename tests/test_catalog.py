"""The README catalog, the workflow pins and the sonar refs must agree.

This is the drift these tests exist to catch: a version bump that updates the
workflow but not the documentation publishes a correct image alongside a README
that lies about it, and nothing else would notice.
"""

from __future__ import annotations

import catalog
import pytest

IMAGES = sorted(catalog.image_specs())


@pytest.mark.parametrize("image", IMAGES)
def test_image_version_is_consistent(image: str) -> None:
    """The workflow pin, sonar ref and README row agree for this image."""
    problems = catalog.problems_for(image)
    assert not problems, "\n".join(str(problem) for problem in problems)


def test_no_contradictions_anywhere() -> None:
    """Nothing is inconsistent, including the parts not tied to one image."""
    problems = catalog.collect_problems()
    assert not problems, "\n".join(str(problem) for problem in problems)


def test_every_catalog_row_has_a_workflow() -> None:
    """The README does not advertise images we do not publish."""
    orphans = sorted(set(catalog.catalog_rows()) - set(catalog.image_specs()))
    assert not orphans, f"README lists images with no workflow: {orphans}"


def test_badge_matches_catalog_size() -> None:
    assert catalog.badge_count() == len(catalog.catalog_rows())


def test_caddy_version_is_documented() -> None:
    pinned, documented = catalog.caddy_versions()
    assert pinned is not None, "caddy.yml has no CADDY_VERSION pin"
    assert pinned == documented


@pytest.mark.parametrize("image", IMAGES)
def test_local_images_have_a_matching_directory(image: str) -> None:
    """A locally built image's context directory exists and is named after it."""
    spec = catalog.image_specs()[image]
    if not spec.is_local_dockerfile:
        pytest.skip(f"{image} is built from an upstream Dockerfile")

    expected = f"files/{image}"
    assert spec.context == expected, (
        f"{spec.workflow} builds context `{spec.context}`; expected `{expected}` "
        "so that image name, directory and workflow filename all match."
    )
    assert (catalog.REPO_ROOT / expected / "Dockerfile").is_file()


@pytest.mark.parametrize("image", IMAGES)
def test_workflow_is_named_after_its_image(image: str) -> None:
    spec = catalog.image_specs()[image]
    assert spec.workflow == f"{image}.yml", (
        f"image `{image}` is published by `{spec.workflow}`; name them alike so the "
        "catalog stays navigable."
    )


@pytest.mark.parametrize("image", IMAGES)
def test_every_image_has_a_smoke_test(image: str) -> None:
    """A published image with no smoke test can break silently per architecture."""
    spec = catalog.image_specs()[image]
    assert spec.has_smoke_command, f"{spec.workflow} declares no smoke-command."


@pytest.mark.parametrize("image", IMAGES)
def test_images_build_for_both_architectures(image: str) -> None:
    spec = catalog.image_specs()[image]
    platforms = spec.platforms or "linux/amd64,linux/arm64"
    assert "linux/amd64" in platforms, f"{spec.workflow} does not target linux/amd64"
    assert "linux/arm64" in platforms, f"{spec.workflow} does not target linux/arm64"
