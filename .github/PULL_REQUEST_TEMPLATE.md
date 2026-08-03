## What changed

<!-- One or two sentences. If this is a version bump, name the old and new version. -->

## Type

- [ ] Upstream version bump
- [ ] Dockerfile change
- [ ] New image
- [ ] CI / pipeline change
- [ ] Documentation

## Checklist

- [ ] The catalog table in `README.md` matches the version pinned in the workflow
- [ ] The `sonar:` job's `upstream-ref:` matches the new version, if the tool has one
- [ ] Built locally for `linux/amd64` and `linux/arm64`, or CI's pull request build passes
- [ ] The image's smoke test still exercises something meaningful
- [ ] No unpinned base images and no actions on mutable refs

## Verification

<!--
Paste the commands you ran and their result, for example:

  docker buildx build --platform linux/arm64 --load -t local/wafw00f files/wafw00f
  docker run --rm local/wafw00f --help
-->
