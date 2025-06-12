# Use an official Python runtime as a parent image
FROM python:3.12.11-slim-bookworm

ENV TZ="Europe/Madrid"

# Instala herramientas necesarias para compilar extensiones en C
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copia solo los archivos necesarios para instalar dependencias primero
COPY requirements.txt /app/

# Instala dependencias antes de copiar el código fuente
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Make port 80 available to the world outside this container
EXPOSE 8005

# Run main.py when the container launches
CMD ["fastapi", "run", "/app/api-chroma/main.py" ,"--host", "0.0.0.0", "--port", "8005"]

