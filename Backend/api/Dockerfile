FROM python:3.10-slim-buster

WORKDIR /app

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y apt-utils && \
    pip install --upgrade pip && \
    apt-get install -y git

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MODULE_NAME=main:app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]