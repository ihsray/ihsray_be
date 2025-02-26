# Use the official Python 3.10 slim image
FROM python:3.10-slim

# This stops Python from buffering its output (helpful for logs)
ENV PYTHONUNBUFFERED=1

# Create a working directory in the container
WORKDIR /app

# Copy your requirements first (for efficient caching)
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Now copy all your project files into the container
COPY . .

# Tell Docker which port to listen on (Cloud Run expects port 8080)
EXPOSE 8080

# Command to run your app with Gunicorn on port 8080
CMD ["gunicorn", "--bind", ":8080", "ihsray_be.wsgi"]