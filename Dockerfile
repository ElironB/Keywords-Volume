# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Install Chromium
RUN apt-get update && apt-get install -y chromium-driver

# Copy the chromedriver executable to the container
COPY chromedriver /app/chromedriver

# Set the executable permission for chromedriver
RUN chmod +x /app/chromedriver

# Make port 1000 available to the world outside this container
EXPOSE 1000

# Define environment variable
ENV NAME World

# Run uvicorn when the container launches
CMD ["uvicorn", "main:main", "--host", "0.0.0.--port", "1000"]
