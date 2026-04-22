# Use an official Python runtime as a parent image
FROM python:3.13-alpine

ARG RELEASE_VERSION="v2.4.2"

# Install git
RUN apk update && apk add --no-cache git

# Set the working directory in the container
WORKDIR /app

# Clone the wafw00f repository
RUN git clone --branch "$RELEASE_VERSION" https://github.com/EnableSecurity/wafw00f .

# Install any needed packages specified in requirements.txt
RUN pip install setuptools

RUN python setup.py install

ENTRYPOINT [ "wafw00f" ]
