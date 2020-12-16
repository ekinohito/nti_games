FROM python:3.8

RUN mkdir -p /home/app

RUN useradd app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
RUN mkdir $APP_HOME/staticfiles
WORKDIR $APP_HOME

COPY . $APP_HOME

RUN pip install -r requirements.txt

RUN chown -R app:app $APP_HOME

USER app

# ENTRYPOINT ["/home/app/web/entrypoint.prod.sh"]
