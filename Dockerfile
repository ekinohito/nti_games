FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev libffi-dev openssl-dev
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /home/app

RUN addgroup -S app && adduser -S app -G app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

COPY ./analytics $APP_HOME/analytics
COPY ./core $APP_HOME/core
COPY ./manage.py $APP_HOME/manage.py
COPY ./nti_games $APP_HOME/nti_games

RUN chown -R app:app $APP_HOME

USER app

# ENTRYPOINT ["/home/app/web/entrypoint.prod.sh"]
