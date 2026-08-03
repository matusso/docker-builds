# syntax=docker/dockerfile:1
#
# PocketBase — open source realtime backend in a single file.
# Upstream: https://github.com/pocketbase/pocketbase
#
# Upstream ships prebuilt binaries but no image. The release archive for the
# target architecture is downloaded and verified against the release's
# `checksums.txt` before being copied into a minimal runtime stage.
#
#   docker build --build-arg RELEASE_VERSION=v0.39.10 -t pocketbase files/pocketbase
#
# ---------------------------------------------------------------------------
# fetch — download and checksum-verify the release archive
# ---------------------------------------------------------------------------
FROM alpine:3.24.1 AS fetch

ARG RELEASE_VERSION=v0.39.10
# Provided automatically by BuildKit; do not override.
ARG TARGETOS
ARG TARGETARCH

RUN apk add --no-cache \
        ca-certificates \
        unzip \
        wget

WORKDIR /tmp/pb

# hadolint ignore=DL3003
RUN set -eux; \
    version="${RELEASE_VERSION#v}"; \
    archive="pocketbase_${version}_${TARGETOS}_${TARGETARCH}.zip"; \
    base="https://github.com/pocketbase/pocketbase/releases/download/${RELEASE_VERSION}"; \
    wget -q -O "${archive}" "${base}/${archive}"; \
    wget -q -O checksums.txt "${base}/checksums.txt"; \
    grep " ${archive}\$" checksums.txt > expected.txt; \
    sha256sum -c expected.txt; \
    unzip -q "${archive}" -d /out; \
    chmod 0755 /out/pocketbase; \
    /out/pocketbase --version

# ---------------------------------------------------------------------------
# runtime
# ---------------------------------------------------------------------------
FROM alpine:3.24.1 AS runtime

ARG RELEASE_VERSION=v0.39.10

LABEL org.opencontainers.image.title="pocketbase" \
      org.opencontainers.image.description="Open source realtime backend in a single file" \
      org.opencontainers.image.version="${RELEASE_VERSION}" \
      org.opencontainers.image.source="https://github.com/pocketbase/pocketbase" \
      org.opencontainers.image.licenses="MIT"

RUN apk add --no-cache ca-certificates

COPY --from=fetch /out/pocketbase /usr/local/bin/pocketbase

RUN addgroup -g 10001 -S pocketbase \
    && adduser -u 10001 -G pocketbase -S -h /pb pocketbase \
    && mkdir -p /pb/pb_data /pb/pb_migrations /pb/pb_hooks \
    && chown -R 10001:10001 /pb

USER 10001:10001
WORKDIR /pb
VOLUME ["/pb/pb_data"]

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["wget", "-q", "-O", "/dev/null", "http://127.0.0.1:8080/api/health"]

ENTRYPOINT ["pocketbase"]
CMD ["serve", "--http=0.0.0.0:8080", "--dir=/pb/pb_data", "--migrationsDir=/pb/pb_migrations", "--hooksDir=/pb/pb_hooks"]
