# syntax=docker/dockerfile:1
#
# masscan — mass IP port scanner.
# Upstream: https://github.com/robertdavidgraham/masscan
#
# Compiled from the tagged release with upstream's Makefile, then copied into a
# clean runtime, so neither git nor the C toolchain reaches the published image.
#
# Two properties of masscan shape this file:
#
#   * It does not link libpcap, it `dlopen`s "libpcap.so" at startup. Alpine
#     ships that unversioned name only in libpcap-dev, so the runtime stage
#     recreates the link against the versioned library from the runtime package.
#   * Scanning needs a raw socket. The binary carries the `cap_net_raw` file
#     capability so the unprivileged default user can scan with no extra flags,
#     NET_RAW being part of Docker's default capability set. Nothing further is
#     stamped onto it deliberately: a file capability outside the container's
#     bounding set makes execve fail with EPERM, which would break a plain
#     `docker run` rather than merely limit it.
#
#   docker build --build-arg RELEASE_VERSION=1.3.2 -t masscan files/masscan
#   docker run --rm --network host masscan -p80,443 192.0.2.0/24 --rate 1000
#
# ---------------------------------------------------------------------------
# build — compile bin/masscan from the tagged release
# ---------------------------------------------------------------------------
FROM alpine:3.24.1 AS build

ARG RELEASE_VERSION=1.3.2
ARG UPSTREAM_GIT=https://github.com/robertdavidgraham/masscan.git

# linux-headers: the route and interface code includes <linux/rtnetlink.h>.
RUN apk add --no-cache build-base git linux-headers

WORKDIR /src

# The clone keeps its tag because the Makefile compiles in `git describe`.
# Upstream's own regression suite runs here, so a broken build fails the
# architecture that produced it rather than the published manifest.
RUN git clone --depth 1 --branch "${RELEASE_VERSION}" "${UPSTREAM_GIT}" . \
    && make -j "$(nproc)" \
    && strip bin/masscan \
    && bin/masscan --selftest

# ---------------------------------------------------------------------------
# runtime
# ---------------------------------------------------------------------------
FROM alpine:3.24.1 AS runtime

ARG RELEASE_VERSION=1.3.2

LABEL org.opencontainers.image.title="masscan" \
      org.opencontainers.image.description="Mass IP port scanner" \
      org.opencontainers.image.version="${RELEASE_VERSION}" \
      org.opencontainers.image.source="https://github.com/robertdavidgraham/masscan" \
      org.opencontainers.image.licenses="AGPL-3.0-only"

COPY --from=build /src/bin/masscan /usr/local/bin/masscan

# `test -e` follows the symlink, so a libpcap soname change fails the build here
# instead of at the first scan. setcap is removed again once it has been used.
RUN apk add --no-cache libpcap \
    && ln -s libpcap.so.1 /usr/lib/libpcap.so \
    && test -e /usr/lib/libpcap.so \
    && apk add --no-cache --virtual .setcap libcap-setcap \
    && setcap cap_net_raw+eip /usr/local/bin/masscan \
    && apk del .setcap

RUN addgroup -g 10001 -S tool \
    && adduser -u 10001 -G tool -S -h /work tool \
    && mkdir -p /work \
    && chown 10001:10001 /work

USER 10001:10001
WORKDIR /work
VOLUME ["/work"]

ENTRYPOINT ["masscan"]
# masscan has no `--help`: `-h` prints four lines of usage and `--nmap` prints
# the full option summary. Both exit 1, as does every other help path upstream.
CMD ["--nmap"]
