FROM python:3.8.12-slim-bullseye
ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/arcgis-dl-app

RUN pip install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . /usr/src/arcgis-dl-app
