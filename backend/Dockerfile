# Use an official Python runtime as a parent image
FROM python:3.11.9-slim-bullseye

ENV TZ="Europe/Madrid"

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Make port 80 available to the world outside this container
EXPOSE 8005

# Run main.py when the container launches
CMD ["fastapi", "run", "/app/api-chroma/main.py" ,"--host", "0.0.0.0", "--port", "8005"]