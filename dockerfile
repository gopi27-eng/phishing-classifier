# Dockerfile

# 1. Base Image: Use a lightweight official Python image
# Python 3.11 is modern and stable
FROM python:3.11-slim

# 2. Set Environment Variables
# Ensures Python output is sent directly to the terminal/logs (good for debugging)
ENV PYTHONUNBUFFERED 1
# Set the port the Flask application will listen on
ENV FLASK_RUN_PORT=5000

# 3. Set Working Directory inside the container
WORKDIR /app

# 4. Copy and Install Dependencies
# Copy only requirements.txt first. This step is cached, speeding up future builds.
COPY requirements.txt /app/

# Install all necessary Python packages (Flask, scikit-learn, pymongo, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy Application Code
# Copy the rest of the project files (src/, .env, main_app.py, etc.) into the container
COPY . /app/

# 6. Expose Port
# Inform Docker that the container will listen on this port
EXPOSE 5000

# 7. Startup Command
# This command is executed when the container starts.
# It runs your Flask API using the correct module-based launch command.
CMD ["python", "-m", "src.main_app"]