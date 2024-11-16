# Use Python 3.8 on Alpine Linux
FROM python:3.8-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the dependency file to the container
COPY requirements.txt .

# Install system dependencies and Python packages
RUN apk add --no-cache --update \
    postgresql-dev gcc python3-dev musl-dev \
    && pip3 install --no-cache-dir -r requirements.txt

# Copy the application source code to the container
COPY . .

# Set the command to run the service
CMD ["python3", "frontend.py"]
