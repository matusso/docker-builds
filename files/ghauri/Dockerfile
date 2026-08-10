# syntax=docker/dockerfile:1
#
# ghauri — advanced SQL injection detection and exploitation tool.
# Upstream: https://github.com/r0oth3x49/ghauri
#
# Upstream publishes neither a container image nor a PyPI package, so the
# tagged source tree is cloned and installed into a virtualenv that is copied
# into a clean runtime stage. Installation goes through `pip install .` rather
# than `setup.py install`, which setuptools removed in v80.
#
#   docker build --build-arg RELEASE_VERSION=1.4.3 -t ghauri files/ghauri
#
# ---------------------------------------------------------------------------
# build — clone the tagged release, install it into /opt/venv
# ---------------------------------------------------------------------------
FROM python:3.15.0rc1-alpine3.24 AS build

ARG RELEASE_VERSION=1.4.3
ARG UPSTREAM_GIT=https://github.com/r0oth3x49/ghauri.git

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PATH=/opt/venv/bin:$PATH

RUN apk add --no-cache git

RUN python -m venv /opt/venv \
    && git clone --depth 1 --branch "${RELEASE_VERSION}" "${UPSTREAM_GIT}" /src \
    && pip install --upgrade pip setuptools wheel \
    && pip install /src \
    && rm -rf /src

# ---------------------------------------------------------------------------
# runtime
# ---------------------------------------------------------------------------
FROM python:3.15.0rc1-alpine3.24 AS runtime

ARG RELEASE_VERSION=1.4.3

LABEL org.opencontainers.image.title="ghauri" \
      org.opencontainers.image.description="Advanced SQL injection detection and exploitation tool" \
      org.opencontainers.image.version="${RELEASE_VERSION}" \
      org.opencontainers.image.source="https://github.com/r0oth3x49/ghauri" \
      org.opencontainers.image.licenses="MIT"

ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=build /opt/venv /opt/venv

RUN addgroup -g 10001 -S tool \
    && adduser -u 10001 -G tool -S -h /work tool \
    && mkdir -p /work \
    && chown 10001:10001 /work

USER 10001:10001
WORKDIR /work
VOLUME ["/work"]

ENTRYPOINT ["ghauri"]
CMD ["--help"]
