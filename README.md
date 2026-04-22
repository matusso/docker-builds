# docker-builds

`docker-builds` is a GitHub Actions driven build repo that publishes ready-to-run container images and a small set of release artifacts for security tooling and adjacent infrastructure.

The main goal is simple: keep commonly used tools available in `ghcr.io/matusso/*` with reproducible build inputs, current upstream versions, and a place to maintain wrapper Dockerfiles when upstream images are missing or not a good fit.

## What This Repository Publishes

- Multi-architecture container images to GitHub Container Registry under `ghcr.io/matusso/<image-name>`.
- Versioned image tags that usually mirror upstream releases, plus a `latest` tag.
- Security and quality automation through GitHub Actions, Snyk image scans, and SonarCloud scans on selected projects.
- A separate GitHub Release workflow for a custom Caddy binary with the Cloudflare DNS module.

## Published Image Catalog

| Image | Upstream project | Current upstream version | Notes |
| --- | --- | --- | --- |
| `binwalk` | [ReFirmLabs/binwalk](https://github.com/ReFirmLabs/binwalk) | `v3.1.0` | Firmware and binary analysis toolkit. Built from the upstream repository and published as a multi-arch image. |
| `dirsearch` | [maurosoria/dirsearch](https://github.com/maurosoria/dirsearch) | `v0.4.3` | Web path and file brute-forcing utility. Built from the upstream repository and published as a multi-arch image. |
| `ghauri` | [r0oth3x49/ghauri](https://github.com/r0oth3x49/ghauri) | `1.4.3` | SQL injection detection and exploitation tool. Built with a local wrapper Dockerfile that clones the tagged upstream release. |
| `kiterunner` | [assetnote/kiterunner](https://github.com/assetnote/kiterunner) | `v1.0.2` | High-speed content discovery and API route enumeration tool. Built locally from source and published as a multi-arch image. |
| `metasploit-framework` | [rapid7/metasploit-framework](https://github.com/rapid7/metasploit-framework) | `6.4.128` | Full Metasploit Framework image built from the upstream repository and published as a multi-arch image. |
| `mvt` | [mvt-project/mvt](https://github.com/mvt-project/mvt) | `v2.7.0` | Mobile Verification Toolkit CLI package. The image installs the pinned PyPI package and defaults to a shell because the toolkit exposes multiple commands. |
| `pocketbase` | [pocketbase/pocketbase](https://github.com/pocketbase/pocketbase) | `v0.37.2` | PocketBase binary image for running the standalone backend service. The image downloads the correct release artifact for the target architecture. |
| `raptor` | [gadievron/raptor](https://github.com/gadievron/raptor) | `main` | RAPTOR security research framework devcontainer image. It tracks upstream `main` and publishes `latest` plus `sha-<commit>` tags for `linux/amd64` and `linux/arm64/v8`. The bundled CodeQL CLI remains amd64-only because upstream release assets are linux64-only. |
| `routersploit` | [threat9/routersploit](https://github.com/threat9/routersploit) | `v3.4.7` | Exploitation framework focused on embedded devices and router targets. Built with a local wrapper Dockerfile from the tagged upstream source. |
| `wafw00f` | [EnableSecurity/wafw00f](https://github.com/EnableSecurity/wafw00f) | `v2.4.2` | Web application firewall fingerprinting tool. Built with a local wrapper Dockerfile from the tagged upstream source. |

## Additional Release Artifact

- `caddy`: a GitHub Release workflow publishes a custom [Caddy](https://github.com/caddyserver/caddy) binary with `github.com/caddy-dns/cloudflare` compiled in. It is currently pinned to `v2.11.2`.

## Tagging Policy

- Most images publish `latest` and an upstream version tag such as `v0.37.2` or `1.4.3`.
- Images that are built per architecture first, such as `binwalk`, `kiterunner`, and `metasploit-framework`, also publish `-amd64` and `-arm64` tags before a multi-arch manifest is assembled.
- `raptor` is commit-tracked rather than release-tracked and publishes `latest` plus `sha-<upstream-commit>`.

## How The Images Are Built

- Some images build directly from the upstream repository or upstream Dockerfile.
- Some images use curated Dockerfiles in `files/` when the upstream project does not provide a suitable container image.
- Version pins live in the workflow files so rebuilds stay reproducible and easier to audit.
- Workflows are triggered on changes to the relevant workflow or local Docker context. `raptor` also has a scheduled refresh because it tracks upstream `main`.

## Using The Images

Pull a specific image:

```bash
docker pull ghcr.io/matusso/<image-name>:<tag>
```

Run it:

```bash
docker run --rm -it ghcr.io/matusso/<image-name>:<tag> [tool-arguments]
```

Examples:

```bash
docker run --rm -it ghcr.io/matusso/dirsearch:v0.4.3 -u https://example.com
docker run --rm -it ghcr.io/matusso/wafw00f:v2.4.2 https://example.com
docker run --rm -it --entrypoint sh ghcr.io/matusso/raptor:latest
```

Notes:

- `pocketbase` exposes port `8080` and starts the PocketBase server by default.
- `mvt` installs multiple CLI entrypoints, so the container defaults to `sh` rather than forcing a single command.
- `raptor` is a development environment style image, not a minimal single-purpose runtime image.
- On `linux/arm64/v8`, the `raptor` image skips the bundled CodeQL CLI because GitHub’s CodeQL CLI release assets are published as `linux64` only.

## Quality And Security Checks

- Container builds are executed in GitHub Actions.
- Selected images are scanned with Snyk and the results are uploaded to GitHub Code Scanning as SARIF.
- Selected upstream source trees are scanned with SonarCloud for maintainability and code quality visibility.

## Contributing

- Add or update a Dockerfile under `files/` when a local wrapper image is needed.
- Update the corresponding workflow pin when you bump an upstream version.
- Open a pull request with the image change and a brief note about the upstream version you are targeting.

## License

This repository contains build automation and wrapper Dockerfiles. Each packaged upstream project keeps its own license terms. Check the upstream repository for the tool you intend to use.
