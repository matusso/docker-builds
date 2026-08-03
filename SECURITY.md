# Security Policy

## Scope

This repository contains build automation. It publishes container images that
package **third-party security tooling**, which this project does not author.

That distinction determines where a report should go:

| Finding | Report to |
| --- | --- |
| A vulnerability in a published image caused by how we build it — wrong permissions, a leaked credential, an unverified download, a mis-scoped workflow token | This repository (see below) |
| A vulnerability in the tool itself | The upstream project, linked in the [catalog](README.md#image-catalog) |
| A vulnerable dependency inside an image | Usually upstream. Open an issue here if we are pinning an old release and a fixed one exists |

## Reporting

Report privately through
[GitHub Security Advisories](https://github.com/matusso/docker-builds/security/advisories/new).
Please do not open a public issue for an undisclosed vulnerability.

Include the image name and tag, the affected architecture, and how to reproduce.
Expect an initial response within five working days.

## Supply chain posture

- **Provenance.** Every published manifest carries a signed
  [build provenance attestation](https://docs.github.com/actions/security-guides/using-artifact-attestations).
  Verify before use:

  ```bash
  gh attestation verify oci://ghcr.io/matusso/<image>:<tag> --owner matusso
  ```

- **Pinned inputs.** Base images are pinned to exact tags. Upstream sources are
  checked out at a tag, or at an immutable commit SHA for the one image that
  tracks a branch. No workflow calls an action on a mutable ref.

- **Least privilege.** Workflows declare `permissions` explicitly. `packages:
  write` is granted only to the jobs that publish, and pull request builds do
  not push at all.

- **Scanning.** Images are scanned with Trivy on publish and results are
  uploaded to GitHub code scanning. Dockerfile misconfiguration is scanned on
  every pull request.

- **Integrity of downloads.** Where an image installs a prebuilt release
  archive, the archive is verified against the publisher's checksum file during
  the build.

### Scanning is reported, not enforced

Trivy findings do not fail a build by default. These images intentionally
package offensive security tooling whose dependency trees we do not control, and
gating on upstream CVEs would simply stop publishing the tools. Findings are
surfaced in code scanning so they can be judged in context. An individual image
can opt into enforcement with the `scan-fail-on:` input.

## A note on intended use

These images package penetration testing and forensics tooling. Use them only
against systems you are authorised to test.
