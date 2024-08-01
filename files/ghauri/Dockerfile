# Use an official Python runtime as a parent image
FROM python:3.12

# Install git
#RUN apt update && apt install -y git 

# Set the working directory in the container
WORKDIR /app

# Clone the Ghauri repository
RUN git clone --branch 1.3.5 https://github.com/r0oth3x49/ghauri.git .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# install
RUN python /app/setup.py build
RUN python /app/setup.py install

# Run the application
CMD ["/usr/local/bin/ghauri"]
