ARG PYTHON_VERSION=${PYTHON_VERSION} \
    RELEASE_VERSION=${RELEASE_VERSION}

# Use an official Python runtime as a parent image
FROM python:${PYTHON_VERSION}-alpine

ENV PYTHON_VERSION=${PYTHON_VERSION} \
    RELEASE_VERSION=${RELEASE_VERSION}
# Install git
RUN apk update && apk add --no-cache git

# Set the working directory in the container
WORKDIR /app

# Clone the Ghauri repository
RUN RELEASE_VERSION="$RELEASE_VERSION" git clone --branch "$RELEASE_VERSION" https://github.com/r0oth3x49/ghauri.git .

# Install any needed packages specified in requirements.txt
RUN pip install setuptools
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# install
RUN python /app/setup.py build
RUN python /app/setup.py install

# Run the application
CMD ["/usr/local/bin/ghauri"]
