FROM python:2.7

RUN mkdir -p /home/espadev/espa-web
WORKDIR /home/espadev/espa-web

COPY setup/requirements.txt /home/espadev/espa-web
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /home/espadev/.usgs/
RUN ln -s /home/espadev/espa-web/run/config.ini /home/espadev/.usgs/.espa_web
ENV ESPAWEB_SETTINGS=/home/espadev/.usgs/.espa_web
ENV ESPA_ENV=dev
ENV ESPA_WEB_EMAIL_RECEIVE="someone@somewhere.com"

COPY . /home/espadev/espa-web

EXPOSE 4001
ENTRYPOINT ["uwsgi", "run/espadev-uwsgi.ini"]
