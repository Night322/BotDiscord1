FROM python:3.11-slim

# Install ffmpeg and ca-certificates
RUN apt-get update && apt-get install -y ffmpeg ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

CMD ["python", "bot.py"] 