# syntax=docker/dockerfile:1
#
# wafw00f — web application firewall fingerprinting toolkit.
# Upstream: https://github.com/EnableSecurity/wafw00f
#
# Installed from the tagged upstream source tree into a virtualenv that is
# copied into a clean runtime stage, so neither git nor a build toolchain ends
# up in the published image.
#
#   docker build --build-arg RELEASE_VERSION=v2.4.2 -t wafw00f files/wafw00f
#
# ---------------------------------------------------------------------------
# build — clone the tagged release, install it into /opt/venv
# ---------------------------------------------------------------------------
FROM python:3.14.7-alpine3.24 AS build

ARG RELEASE_VERSION=v2.4.2
ARG UPSTREAM_GIT=https://github.com/EnableSecurity/wafw00f.git

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
FROM python:3.14.7-alpine3.24 AS runtime

ARG RELEASE_VERSION=v2.4.2

LABEL org.opencontainers.image.title="wafw00f" \
      org.opencontainers.image.description="Web application firewall fingerprinting toolkit" \
      org.opencontainers.image.version="${RELEASE_VERSION}" \
      org.opencontainers.image.source="https://github.com/EnableSecurity/wafw00f" \
      org.opencontainers.image.licenses="BSD-3-Clause"

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

ENTRYPOINT ["wafw00f"]
CMD ["--help"]
