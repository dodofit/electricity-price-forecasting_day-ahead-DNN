FROM python:3.10

COPY requirements_.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

WORKDIR /app

