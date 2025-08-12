# Stage 1: Builder
# This stage installs the Python dependencies to be cached.
FROM python:3.11-slim as builder

# Set the working directory
WORKDIR /app

# Create a virtual environment to isolate our dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final production image
# This stage builds the final, lightweight production image.
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set the PATH to include the virtual environment's binaries
ENV PATH="/opt/venv/bin:$PATH"

# Copy the application code into the container
COPY ./app /app/

# Expose port 8000 to allow communication with the application
EXPOSE 8000

# Command to run the FastAPI application using Uvicorn
# This assumes an 'app' instance exists in an 'app/main.py' file.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
