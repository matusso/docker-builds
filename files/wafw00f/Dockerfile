# Use an official Python runtime as a parent image
FROM python:3.13-alpine


COPY --link src/wafw00f/ /app
# Set the working directory in the container
WORKDIR /app

# Update
RUN apk update

# Install any needed packages specified in requirements.txt
RUN pip install setuptools

RUN python setup.py install

ENTRYPOINT [ "wafw00f" ]