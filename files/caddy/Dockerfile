# syntax=docker/dockerfile:1
#
# Caddy — custom build with the Cloudflare DNS module compiled in.
# Upstream: https://github.com/caddyserver/caddy
#
# Built with xcaddy from the same pins as the binary release in
# .github/workflows/caddy.yml, so the image and the release assets carry the
# same Caddy, module set and Go toolchain. The runtime stage mirrors the layout
# of the official `caddy` image (/etc/caddy, /config, /data, /srv), so it is a
# drop-in replacement — except that it runs as an unprivileged user.
#
#   docker build --build-arg RELEASE_VERSION=v2.11.7 -t caddy files/caddy
#
# ---------------------------------------------------------------------------
# build — compile caddy with xcaddy
# ---------------------------------------------------------------------------
FROM golang:1.27.3-alpine3.24 AS build

ARG RELEASE_VERSION=v2.11.7
ARG XCADDY_VERSION=v0.4.7
ARG CADDY_MODULES=github.com/caddy-dns/cloudflare

ENV CGO_ENABLED=0 \
    XCADDY_GO_BUILD_FLAGS="-ldflags '-w -s' -trimpath"

RUN apk add --no-cache git libcap-setcap

RUN go install "github.com/caddyserver/xcaddy/cmd/xcaddy@${XCADDY_VERSION}"

WORKDIR /src

# hadolint ignore=SC2086
RUN set -eux; \
    with=""; \
    for module in ${CADDY_MODULES}; do with="${with} --with ${module}"; done; \
    xcaddy build "${RELEASE_VERSION}" --output /out/caddy ${with}; \
    /out/caddy version; \
    /out/caddy list-modules | grep -q '^dns.providers.cloudflare$'; \
    # Grant the capability here: doing it in the runtime stage rewrites the
    # binary into a second layer. COPY --from preserves the xattr.
    setcap cap_net_bind_service=+ep /out/caddy

# ---------------------------------------------------------------------------
# runtime
# ---------------------------------------------------------------------------
FROM alpine:3.24.3 AS runtime

ARG RELEASE_VERSION=v2.11.7

LABEL org.opencontainers.image.title="caddy" \
      org.opencontainers.image.description="Caddy web server with the Cloudflare DNS module" \
      org.opencontainers.image.version="${RELEASE_VERSION}" \
      org.opencontainers.image.source="https://github.com/caddyserver/caddy" \
      org.opencontainers.image.licenses="Apache-2.0"

# mailcap provides /etc/mime.types for file_server; tzdata lets TZ work.
RUN apk add --no-cache \
        ca-certificates \
        mailcap \
        tzdata

COPY --from=build /out/caddy /usr/bin/caddy
COPY Caddyfile /etc/caddy/Caddyfile

# The binary carries cap_net_bind_service (set in the build stage) so the
# unprivileged user can still listen on 80/443. Docker grants it by default.
RUN addgroup -g 10001 -S caddy \
    && adduser -u 10001 -G caddy -S -h /srv caddy \
    && mkdir -p /config/caddy /data/caddy /srv \
    && chown -R 10001:10001 /config /data /srv

ENV XDG_CONFIG_HOME=/config \
    XDG_DATA_HOME=/data

USER 10001:10001
WORKDIR /srv
VOLUME ["/config", "/data"]

EXPOSE 80 443 443/udp 2019

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
