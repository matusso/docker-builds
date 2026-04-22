# Use an official Python runtime as a parent image
FROM python:3.13-alpine

ARG RELEASE_VERSION="v2.4.2"

# Install git
RUN apk update && apk add --no-cache git

# Set the working directory in the container
WORKDIR /app

# Clone the wafw00f repository
RUN git clone --depth=1 --branch "$RELEASE_VERSION" https://github.com/EnableSecurity/wafw00f .

# Install wafw00f from the upstream pyproject-based package.
RUN pip install --no-cache-dir .

ENTRYPOINT [ "wafw00f" ]
