FROM python:3.7

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /srv/www/nti
WORKDIR /srv/www/nti

RUN pip install -r requirements.txt
