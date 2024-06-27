# Use Ubuntu 22.04 as a base image
FROM ubuntu:22.04

# Set the working directory in the container
WORKDIR /app

# Update and install Python and pip
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Specify entrypoint if needed, but no need to run Jupyter
CMD ["bash"]
