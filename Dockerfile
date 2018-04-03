# ==========+ Source Code dependencies +==========
FROM python:3.6-slim as application
RUN apt-get update && apt-get install -y gcc

RUN useradd espadev
WORKDIR /home/espadev/espa-web
COPY setup.py version.txt README.md /home/espadev/espa-web/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e .

COPY ./src/ /home/espadev/espa-web/src/
COPY ./run/ /home/espadev/espa-web/run/

ENV ESPAWEB_SETTINGS=/home/espadev/.usgs/espaweb-settings.ini \
    ESPA_ENV=dev \
    ESPA_WEB_EMAIL_RECEIVE="someone@somewhere.com" \
    ESPA_API_HOST="http://localhost:4004/api/v1"

USER espadev
EXPOSE 4001
ENTRYPOINT ["uwsgi", "run/uwsgi.ini"]

# ==========+ Unit testing dependencies +==========
FROM python:3.6-slim  as tester
WORKDIR /home/espadev/espa-web
COPY --from=application /home/espadev/espa-web /home/espadev/espa-web/
COPY --from=application /usr/local/lib/python3.6/site-packages /usr/local/lib/python3.6/site-packages

RUN pip install -e .[test]
COPY ./test/ ./test/
ENTRYPOINT ["pytest", "--cov=./"]
