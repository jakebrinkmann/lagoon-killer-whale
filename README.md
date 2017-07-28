[![Build Status](https://travis-ci.org/USGS-EROS/espa-web.svg?branch=master)](https://travis-ci.org/USGS-EROS/espa-web)

## espa-web
This project serves up the espa website and provides all the job ordering &
scheduling functions, by being a Graphical User Interface (GUI) for the [ESPA-API](https://github.com/USGS-EROS/espa-api). 
This code is provided as reference only; internal EROS services are not externally available and their source code are not publicly available.

Access the site at [`https://espa.cr.usgs.gov/login`](https://espa.cr.usgs.gov/login).

### Quick Links
* [Home](https://espa.cr.usgs.gov/index)
* [New Order](https://espa.cr.usgs.gov/ordering/new)
* [Pending Orders](https://espa.cr.usgs.gov/ordering/status/)

## Developers

If you want to run this web interface locally, use the included Dockerfile to 
help get started: 

#### Environment
```bash
export ESPA_API_HOST='https://espa.cr.usgs.gov/api/v1'
export ESPA_MEMCACHE_HOST='localhost:30090'
export ESPAWEB_SETTINGS="${PWD}/run/config.ini"
export ESPA_WEB_EMAIL_RECEIVE="{my email address}"
```
#### Services
```bash
docker-compose -f setup/docker-compose.yml up -d
```
#### Building/Running
```bash
docker build -t espa-web .
docker run -it -p 127.0.0.1:4004:4004 -p 127.0.0.1:30090:30090 espa-web
```
#### Testing
```bash
docker run -it --entrypoint run/runtests espa-web
```

