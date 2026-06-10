# Intentionally vulnerable Dockerfile for educational purposes
FROM python:3.9.7-slim

# VULN: No USER instruction (runs as root)
# VULN: No HEALTHCHECK
# VULN: Using COPY . . (copies everything)
# VULN: Not using multi-stage build

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# VULN: Debug mode in CMD
CMD ["python", "app/main.py"]
