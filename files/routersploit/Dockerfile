# Use an official Python runtime as a parent image
FROM python:3.13-alpine

ARG RELEASE_VERSION="v3.4.7"

# Install git
RUN apk update && apk add --no-cache git

# Set the working directory in the container
WORKDIR /app

# Clone the RouterSploit repository
RUN git clone --branch "$RELEASE_VERSION" https://github.com/threat9/routersploit .

# Install any needed packages specified in requirements.txt
RUN pip install setuptools telnetlib-313-and-up
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# install
RUN python /app/setup.py build
RUN python /app/setup.py install

# Run the application
CMD ["/usr/local/bin/rsf.py"]
