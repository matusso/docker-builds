# syntax=docker/dockerfile:1
#
# commix — automated OS command injection detection and exploitation tool.
# Upstream: https://github.com/commixproject/commix
#
# Upstream publishes no container image. commix needs only the standard
# library, so the tagged source tree is cloned, stripped of its .git directory
# and copied into a clean runtime stage — no virtualenv required.
#
# The image runs upstream's `commix.py` launcher rather than the `commix`
# console script: v4.1's setup.py points that script at a function that does
# not exist until a later release, so a pip-installed `commix` crashes.
#
# commix writes session data and results to `.output/` relative to the working
# directory, i.e. /work.
#
#   docker build --build-arg RELEASE_VERSION=v4.1 -t commix files/commix
#
# ---------------------------------------------------------------------------
# build — clone the tagged release into /opt/commix
# ---------------------------------------------------------------------------
FROM python:3.16.0a1-alpine3.24 AS build

ARG RELEASE_VERSION=v4.1
ARG UPSTREAM_GIT=https://github.com/commixproject/commix.git

RUN apk add --no-cache git

RUN git clone --depth 1 --branch "${RELEASE_VERSION}" "${UPSTREAM_GIT}" /opt/commix \
    && rm -rf /opt/commix/.git

# ---------------------------------------------------------------------------
# runtime
# ---------------------------------------------------------------------------
FROM python:3.16.0a1-alpine3.24 AS runtime

ARG RELEASE_VERSION=v4.1

LABEL org.opencontainers.image.title="commix" \
      org.opencontainers.image.description="Automated OS command injection detection and exploitation tool" \
      org.opencontainers.image.version="${RELEASE_VERSION}" \
      org.opencontainers.image.source="https://github.com/commixproject/commix" \
      org.opencontainers.image.licenses="GPL-3.0-or-later"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=build /opt/commix /opt/commix

RUN addgroup -g 10001 -S tool \
    && adduser -u 10001 -G tool -S -h /work tool \
    && mkdir -p /work \
    && chown 10001:10001 /work

USER 10001:10001
WORKDIR /work
VOLUME ["/work"]

ENTRYPOINT ["python", "/opt/commix/commix.py"]
CMD ["--help"]
