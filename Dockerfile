FROM --platform=linux/amd64 python:3.8-slim-buster

WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000


CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

