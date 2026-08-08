FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt && rm -rf requirements.txt
COPY ./src /app/src
WORKDIR /app/src
CMD ["python", "main.py"]