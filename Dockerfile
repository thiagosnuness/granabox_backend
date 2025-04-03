FROM python:3.11-slim

# Application directory in Docker
WORKDIR /app

# Copy all files from the backend into Docker
COPY . /app

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Flask application port
EXPOSE 5000

# Command to start the application
CMD ["python", "app.py"]