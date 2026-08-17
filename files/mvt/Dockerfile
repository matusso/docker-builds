# syntax=docker/dockerfile:1
#
# MVT (Mobile Verification Toolkit) — forensic analysis of Android and iOS
# devices for signs of compromise.
# Upstream: https://github.com/mvt-project/mvt
#
# Installed from the pinned PyPI release into a virtualenv that is copied into
# a clean runtime stage. MVT exposes two console entrypoints (`mvt-ios` and
# `mvt-android`), so the image defaults to a shell rather than forcing one.
#
#   docker build --build-arg RELEASE_VERSION=v2026.7.29 -t mvt files/mvt
#
# ---------------------------------------------------------------------------
# build — install the pinned PyPI release into /opt/venv
# ---------------------------------------------------------------------------
FROM python:3.14.7-alpine3.24 AS build

ARG RELEASE_VERSION=v2026.7.29

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_ROOT_USER_ACTION=ignore \
    PATH=/opt/venv/bin:$PATH

# MVT pulls in C and Rust extensions (cryptography, pydantic-core,
# pyahocorasick, libusb1). Most ship musllinux wheels; these packages cover the
# architectures and releases where they do not.
RUN apk add --no-cache \
        build-base \
        bzip2-dev \
        cargo \
        libffi-dev \
        libusb-dev \
        openssl-dev \
        python3-dev \
        zstd-dev

RUN python -m venv /opt/venv \
    && pip install --upgrade pip setuptools wheel \
    && pip install "mvt==${RELEASE_VERSION#v}"

# ---------------------------------------------------------------------------
# runtime
# ---------------------------------------------------------------------------
FROM python:3.14.7-alpine3.24 AS runtime

ARG RELEASE_VERSION=v2026.7.29

LABEL org.opencontainers.image.title="mvt" \
      org.opencontainers.image.description="Mobile Verification Toolkit — forensic analysis of Android and iOS devices" \
      org.opencontainers.image.version="${RELEASE_VERSION}" \
      org.opencontainers.image.source="https://github.com/mvt-project/mvt" \
      org.opencontainers.image.licenses="LicenseRef-MVT-1.1"

ENV PATH=/opt/venv/bin:$PATH \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Shared libraries the extension modules dlopen at runtime.
RUN apk add --no-cache \
        libmagic \
        libusb \
        libstdc++ \
        zstd-libs

COPY --from=build /opt/venv /opt/venv

RUN addgroup -g 10001 -S tool \
    && adduser -u 10001 -G tool -S -h /work tool \
    && mkdir -p /work \
    && chown 10001:10001 /work

USER 10001:10001
WORKDIR /work
VOLUME ["/work"]

CMD ["sh"]
