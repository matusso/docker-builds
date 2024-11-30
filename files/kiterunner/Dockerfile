# Use Alpine Linux as the base image
FROM alpine:latest

# Set environment variables
ENV KR_VERSION="v1.0.2" \
    KR_DIR="/usr/local/kiterunner"

# Install dependencies
RUN apk add --no-cache \
    bash \
    build-base \
    git \
    go \
    && mkdir -p "$KR_DIR"

# Clone kiterunner repository and build
WORKDIR $KR_DIR
RUN git clone --depth=1 --branch "$KR_VERSION"  https://github.com/assetnote/kiterunner.git . \
    && make build \
    && ln -s $(pwd)/dist/kr /usr/local/bin/kr

# Add a volume for wordlists and routes
VOLUME ["/data"]

# Set the default working directory
WORKDIR /data

# Set kr as the entrypoint
ENTRYPOINT ["kr"]

# Add an example instruction for users
CMD ["--help"]
