# syntax=docker/dockerfile:1
#
# RouterSploit — exploitation framework for embedded devices.
# Upstream: https://github.com/threat9/routersploit
#
# Two notes on the build:
#   * `telnetlib-313-and-up` restores the stdlib `telnetlib` module that Python
#     3.13 removed (PEP 594) and that RouterSploit still imports.
#   * Installation goes through `pip install .`; upstream's `setup.py install`
#     path no longer works with setuptools >= 80.
#
#   docker build --build-arg RELEASE_VERSION=v3.4.7 -t routersploit files/routersploit
#
# ---------------------------------------------------------------------------
# build — clone the tagged release, install it into /opt/venv
# ---------------------------------------------------------------------------
FROM python:3.14.6-alpine3.24 AS build

ARG RELEASE_VERSION=v3.4.7
ARG UPSTREAM_GIT=https://github.com/threat9/routersploit.git
ARG TELNETLIB_SHIM_VERSION=3.13.1

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PATH=/opt/venv/bin:$PATH

# build-base/libffi-dev/openssl-dev cover the source builds that remain when a
# dependency publishes no musllinux wheel for the target architecture.
RUN apk add --no-cache \
        build-base \
        git \
        libffi-dev \
        openssl-dev

RUN python -m venv /opt/venv \
    && git clone --depth 1 --branch "${RELEASE_VERSION}" "${UPSTREAM_GIT}" /src \
    && pip install --upgrade pip setuptools wheel \
    && pip install "telnetlib-313-and-up==${TELNETLIB_SHIM_VERSION}" \
    && pip install /src \
    && rm -rf /src

# ---------------------------------------------------------------------------
# runtime
# ---------------------------------------------------------------------------
FROM python:3.14.6-alpine3.24 AS runtime

ARG RELEASE_VERSION=v3.4.7

LABEL org.opencontainers.image.title="routersploit" \
      org.opencontainers.image.description="Exploitation framework for embedded devices" \
      org.opencontainers.image.version="${RELEASE_VERSION}" \
      org.opencontainers.image.source="https://github.com/threat9/routersploit" \
      org.opencontainers.image.licenses="BSD-3-Clause"

ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apk add --no-cache libstdc++

COPY --from=build /opt/venv /opt/venv

RUN addgroup -g 10001 -S tool \
    && adduser -u 10001 -G tool -S -h /work tool \
    && mkdir -p /work \
    && chown 10001:10001 /work

USER 10001:10001
WORKDIR /work
VOLUME ["/work"]

ENTRYPOINT ["rsf.py"]
