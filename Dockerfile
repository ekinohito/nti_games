FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /var/www/nti
WORKDIR /var/www/nti

RUN pip install -r requirements.txt
