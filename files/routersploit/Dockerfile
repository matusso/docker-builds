# Use an official Python runtime as a parent image
FROM python:3.13-alpine

# Set the working directory in the container
WORKDIR /app

# Copy the RouterSploit source code from the submodule
COPY --link src/routersploit/ /app

# Update
RUN apk update

# Install any needed packages specified in requirements.txt
RUN pip install setuptools telnetlib-313-and-up
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Build and install the package
RUN python /app/setup.py build
RUN python /app/setup.py install

# Run the application
CMD ["/usr/local/bin/rsf.py"]
