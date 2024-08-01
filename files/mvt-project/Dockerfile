# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    libusb-1.0-0 \
    libbz2-dev \
    libzstd-dev \
    && rm -rf /var/lib/apt/lists/*

# Install mvt via pip
RUN pip install --no-cache-dir mvt

# Run a shell by default (for testing and usage)
CMD ["bash"]
