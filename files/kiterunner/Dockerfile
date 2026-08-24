# syntax=docker/dockerfile:1
#
# kiterunner (kr) — contextual content discovery and API route enumeration.
# Upstream: https://github.com/assetnote/kiterunner
#
# Built from tagged source. Upstream's `make build` passes
# `-extld g++ -extldflags -static`, which needs a full C toolchain and does not
# link cleanly against musl; `go build` is invoked directly with CGO disabled
# instead. The version metadata upstream injects via ldflags is preserved, using
# the commit date so the build stays reproducible.
#
#   docker build --build-arg RELEASE_VERSION=v1.0.2 -t kiterunner files/kiterunner
#
# ---------------------------------------------------------------------------
# build — compile a static kr binary
# ---------------------------------------------------------------------------
FROM golang:1.27.0-alpine3.24 AS build

ARG RELEASE_VERSION=v1.0.2
ARG UPSTREAM_GIT=https://github.com/assetnote/kiterunner.git
ARG LDFLAGS_PKG=github.com/assetnote/kiterunner/cmd/kiterunner/cmd

ENV CGO_ENABLED=0 \
    GOOS=linux \
    GOFLAGS=-buildvcs=false

RUN apk add --no-cache git

WORKDIR /src

RUN git clone --depth 1 --branch "${RELEASE_VERSION}" "${UPSTREAM_GIT}" . \
    && commit="$(git rev-parse HEAD)" \
    && date="$(git log -1 --format=%cI)" \
    && go build -trimpath \
        -ldflags "-s -w \
            -X '${LDFLAGS_PKG}.Version=${RELEASE_VERSION}' \
            -X '${LDFLAGS_PKG}.Commit=${commit}' \
            -X '${LDFLAGS_PKG}.Date=${date}'" \
        -o /out/kr ./cmd/kiterunner \
    && /out/kr version

# ---------------------------------------------------------------------------
# runtime
# ---------------------------------------------------------------------------
FROM alpine:3.24.1 AS runtime

ARG RELEASE_VERSION=v1.0.2

LABEL org.opencontainers.image.title="kiterunner" \
      org.opencontainers.image.description="Contextual content discovery and API route enumeration tool" \
      org.opencontainers.image.version="${RELEASE_VERSION}" \
      org.opencontainers.image.source="https://github.com/assetnote/kiterunner" \
      org.opencontainers.image.licenses="AGPL-3.0-only"

RUN apk add --no-cache ca-certificates

COPY --from=build /out/kr /usr/local/bin/kr

RUN addgroup -g 10001 -S tool \
    && adduser -u 10001 -G tool -S -h /data tool \
    && mkdir -p /data \
    && chown 10001:10001 /data

USER 10001:10001
WORKDIR /data
VOLUME ["/data"]

ENTRYPOINT ["kr"]
CMD ["--help"]
