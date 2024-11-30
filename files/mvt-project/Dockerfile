# Use an official Python runtime for Alpine as the base image
FROM python:3.13-alpine

# Set the working directory in the container
WORKDIR /

# Install necessary Alpine packages and dependencies
RUN apk add --no-cache \
    libmagic \
    libusb \
    bzip2-dev \
    zstd-dev \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev

# Install mvt via pip
RUN pip install --no-cache-dir mvt

# Run a shell by default (for testing and usage)
CMD ["sh"]
