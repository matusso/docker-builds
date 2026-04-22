FROM alpine:latest

ARG PB_VERSION=v0.37.2
ARG TARGETOS=linux
ARG TARGETARCH

RUN apk add --no-cache \
    unzip \
    ca-certificates \
    wget

# download and unzip PocketBase
RUN PB_VERSION_NO_V="${PB_VERSION#v}" \
    && wget -O /tmp/pb.zip "https://github.com/pocketbase/pocketbase/releases/download/${PB_VERSION}/pocketbase_${PB_VERSION_NO_V}_${TARGETOS}_${TARGETARCH}.zip" \
    && unzip /tmp/pb.zip -d /pb/ \
    && rm -f /tmp/pb.zip

# uncomment to copy the local pb_migrations dir into the image
# COPY ./pb_migrations /pb/pb_migrations

# uncomment to copy the local pb_hooks dir into the image
# COPY ./pb_hooks /pb/pb_hooks

EXPOSE 8080

# start PocketBase
CMD ["/pb/pocketbase", "serve", "--http=0.0.0.0:8080"]
