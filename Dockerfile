# Use a lightweight Python base image
FROM python:3.14-slim

# Prevent Python from writing .pyc files and keep stdout unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the project files into the container
COPY . /app/

# Install the package
RUN pip install --no-cache-dir .

# Set the entrypoint to the CLI.
# This means `docker run ghcr.io/adkinsrs/hub2gos` will implicitly call your CLI.
ENTRYPOINT ["python", "-m", "hub2gos.cli"]