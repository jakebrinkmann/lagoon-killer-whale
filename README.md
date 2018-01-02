
## espa-web  [![build status][0]][1] [![Codecov branch][2]][3]

This project serves up the espa website and provides all the job ordering &
scheduling functions, by being a Graphical User Interface (GUI) for the [ESPA-API](https://github.com/USGS-EROS/espa-api). 
This code is provided as reference only; internal EROS services are not externally available and their source code are not publicly available.

Access the site at [`https://espa.cr.usgs.gov/`][4].

### Quick Links
* [Home][5]
* [New Order][6]
* [Pending Orders][7]

## Developers

If you want to run this web interface locally, use the included Dockerfile to 
help get started: 

#### Services
```bash
docker-compose -f setup/docker-compose.yml up -d
```
#### Building/Running
```bash
docker build -t espa-web .
docker run -it -p 127.0.0.1:4001:4001 \
    --net setup_default --link setup_memcached_1 \
    -e ESPA_API_HOST='https://espa.cr.usgs.gov/api/v1' \
    -e ESPA_MEMCACHE_HOST='localhost:11211' \ 
    -e ESPAWEB_SETTINGS='./run/config.ini' \
    -e ESPA_WEB_EMAIL_RECEIVE="{my email address}" espa-web
```
#### Testing
```bash
docker exec -it {running container id} run/runtests
```


#### Support Information

This project is unsupported software provided by the U.S. Geological Survey (USGS) Earth Resources Observation and Science (EROS) Land Satellite Data Systems (LSDS) Project. For questions regarding products produced by this source code, please contact us at [custserv@usgs.gov][8].

#### Disclaimer

This software is preliminary or provisional and is subject to revision. It is being provided to meet the need for timely best science. The software has not received final approval by the U.S. Geological Survey (USGS). No warranty, expressed or implied, is made by the USGS or the U.S. Government as to the functionality of the software and related material nor shall the fact of release constitute any such warranty. The software is provided on the condition that neither the USGS nor the U.S. Government shall be held liable for any damages resulting from the authorized or unauthorized use of the software.
    

[0]: https://img.shields.io/travis/USGS-EROS/espa-web/master.svg?style=flat-square
[1]: https://travis-ci.org/USGS-EROS/espa-web
[2]: https://img.shields.io/codecov/c/github/USGS-EROS/espa-web/master.svg?style=flat-square
[3]: https://codecov.io/gh/USGS-EROS/espa-web
[4]: https://espa.cr.usgs.gov/
[5]: https://espa.cr.usgs.gov/index
[6]: https://espa.cr.usgs.gov/ordering/new
[7]: https://espa.cr.usgs.gov/ordering/status/
[8]: mailto:custserv@usgs.gov

