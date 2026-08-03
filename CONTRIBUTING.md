# Contributing

This repository builds and publishes container images for third-party security
tooling. Almost every change falls into one of three shapes, described below.

## Bumping an upstream version

1. Edit the `version:` input in the tool's workflow, for example
   `.github/workflows/wafw00f.yml`.
2. If the tool has a `sonar:` job, update its `upstream-ref:` to match.
3. Update the version in the catalog table in [`README.md`](README.md).
4. Open a pull request. CI builds the image for `linux/amd64` and `linux/arm64`
   and runs its smoke test without publishing anything.

Nothing else needs touching — tags, labels, the manifest list, the provenance
attestation and the vulnerability scan are all handled by the shared pipeline.

## Changing a Dockerfile

Dockerfiles we own live in `files/<image>/Dockerfile` and follow one shape:

- `# syntax=docker/dockerfile:1` on line one.
- A header comment naming the tool, linking upstream, and explaining anything
  non-obvious about the build.
- Base images pinned literally (`FROM python:3.14.6-alpine3.24`). Do not move
  the version into an `ARG` — Dependabot cannot resolve ARG interpolation in a
  `FROM` line and will silently stop updating the image.
- A `build` (or `fetch`) stage that does the compiling or downloading, and a
  `runtime` stage that receives only the finished artifact. Build toolchains and
  `git` must not reach the published image.
- `ARG RELEASE_VERSION` with a default, so the Dockerfile builds standalone. The
  pipeline passes this automatically from the workflow's `version:` input.
- OCI labels: `title`, `description`, `version`, `source`, `licenses`.
- A non-root user, uid/gid `10001`, owning the working directory.

Build it locally before opening a pull request:

```bash
docker buildx build --platform linux/amd64 --load -t local/wafw00f files/wafw00f
docker run --rm local/wafw00f --help
```

## Adding a new image

1. Create `files/<image>/Dockerfile` following the shape above, or plan to build
   from the upstream Dockerfile directly.
2. Create `.github/workflows/<image>.yml` as a caller of
   `_build-image.yml`. Copy an existing one — `wafw00f.yml` is the smallest.
3. Give it a `smoke-command`. It receives `$IMAGE` and must exit `0`.
4. Add a row to the catalog table in `README.md`.

## Tests

The suite in `tests/` asserts the repository's *declared state* rather than
running containers — container behaviour is covered by the per-architecture
smoke tests in the build pipeline. It checks that:

- every Dockerfile in `files/` follows the template above (pinned base, multi-stage,
  OCI labels, non-root, no build toolchain in the runtime stage);
- every workflow keeps its supply-chain guarantees (no mutable action refs,
  explicit `permissions`, per-job timeouts, no publishing from a pull request);
- the RAPTOR patcher applies, is idempotent, tolerates an upstream fix to an
  optional patch, and fails loudly on a missing required one;
- the version pinned in each workflow, its sonar `upstream-ref`, and the README
  catalog table all agree.

That last one is the check that stops documentation drift, which is otherwise
invisible: the image publishes correctly while the README quietly lies.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
pytest -rs
```

The catalog consistency check also has a dependency-free entry point, so you can
run it without a virtualenv:

```bash
python3 scripts/check_catalog.py
```

Both share one implementation in `scripts/catalog.py`, so they cannot disagree.

## Local checks

CI runs these on every pull request; running them first is faster than waiting.

```bash
# Dockerfiles
docker run --rm -i -v "$PWD/.hadolint.yaml:/.hadolint.yaml:ro" \
  hadolint/hadolint hadolint --config /.hadolint.yaml - < files/wafw00f/Dockerfile

# Workflows (also shellchecks every run: block)
docker run --rm -v "$PWD:/repo" --workdir /repo rhysd/actionlint:1.7.12 -color

# YAML
pipx run yamllint --strict --config-file .yamllint.yml .

# Python
pipx run ruff check scripts tests && pipx run ruff format --check scripts tests
```

## Commit messages

Conventional Commits, matching the existing history:

```
feat(pocketbase): verify release archive checksum
fix(raptor): stop hard-failing on obsolete Dockerfile patches
build(deps): bump alpine from 3.24.0 to 3.24.1
ci: add reusable image pipeline
docs: rewrite catalog table
```

## What we do not accept

- Unpinned base images (`:latest`) or unpinned actions on mutable refs
  (`@master`, `@main`).
- Forks of upstream source. If an upstream Dockerfile needs changing for CI,
  patch it at build time with a declarative, reviewable script — see
  `scripts/patch_raptor_dockerfile.py`.
- New images without a smoke test.
