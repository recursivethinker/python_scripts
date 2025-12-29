# Dockerfile for building a portable Linux executable
# Use an official Python image based on an older Debian (Bullseye) for broad glibc compatibility.
FROM python:3.12-slim-bullseye

# Set the working directory inside the container
WORKDIR /app

# Install binutils, which provides 'objdump', a PyInstaller dependency on Linux.
RUN apt-get update && apt-get install -y binutils

# Copy requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install all dependencies from your requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application source code into the container
COPY . .

# Define the command that will be run to build the application
CMD ["pyinstaller", "simpleagent.spec"]
