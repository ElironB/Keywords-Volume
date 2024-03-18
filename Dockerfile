# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Chromium and ChromeDriver along with any other dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 1000 available to the world outside this container
EXPOSE 1000

# Define environment variable for the app to use
ENV NAME World

# Specify paths for Chromium (adjust if needed)
ENV CHROMIUM_PATH /usr/bin/chromium

# Run uvicorn when the container launches
CMD ["uvicorn", "main:main", "--host", "0.0.0.0", "--port", "1000"]
