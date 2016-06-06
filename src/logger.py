import os
import logging

from logging import FileHandler
from logging import Formatter
from logging import Filter
from logging.handlers import SMTPHandler

if not os.path.exists("../logs"):
    os.mkdir("../logs")

LOG_FORMAT = ('%(asctime)s [%(levelname)s]: %(message)s in %(pathname)s:%(lineno)d')


class DbgFilter(Filter):
    def filter(self, rec):
        return rec.levelno == logging.DEBUG

ilogger = logging.getLogger("espa-web")
ilogger.setLevel(logging.DEBUG)

ih = FileHandler("/var/log/uwsgi/espa-web-info.log")
dh = FileHandler("/var/log/uwsgi/espa-web-debug.log")
eh = SMTPHandler(mailhost='localhost', fromaddr='espa@usgs.gov', toaddrs='gs-n-edc_espa_api@usgs.gov', subject='ESPA WEB ERROR')

ih.setLevel(logging.INFO)
dh.setLevel(logging.DEBUG)
eh.setLevel(logging.DEBUG)

for handler in [ih, dh, eh]:
    ilogger.addHandler(handler)

    if isinstance(handler, logging.FileHandler):
        handler.setFormatter(Formatter(LOG_FORMAT))

    if handler.level == logging.DEBUG:
        handler.addFilter(DbgFilter())
