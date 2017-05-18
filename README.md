## espa-web
This project serves up the espa website and provides all the job ordering &
scheduling functions.  This code is provided as reference only; internal EROS services are not externally available and their source code are not publicly available.

## Installation
* Clone this project: `git clone https://github.com/USGS-EROS/espa-web.git espa-web`
* Satisfy system dependencies listed in system-requirements.txt
* Create a virtualenv: `cd espa-web; virtualenv .`
* Install dependencies: `. bin/activate; pip install -r requirements.txt`
* Set `ESPA_DEBUG` env var to either True or False
* Set `ESPA_LOG_DIR` env var.  Defaults to `/var/log/uwsgi/`
* Set `ESPA_CONFIG_FILE` env var to point to db values (defaults to `~/.cfgnfo`)
* Apply database migrations: `python ./manage.py migrate`
* Dump the system configuration: `python ./manage.py shell; from ordering import core; core.dump_config('/dir/file.txt')`
* Edit `file.txt` and then: `python ./manage.py shell; from ordering import core; core.load_config('/dir/file.txt')`

##### Required db & app config in ESPA_CONFIG_FILE
```
[config]
dbhost=your db host
dbport=your port (3306, 5432, etc)
db=your db name (espa)
dbuser=your db user
dbpass=your db password
key=your secret key (for Django)
```

## Testing
Unit tests are included for the application to ensure system integrity.
The tests may be run without fear of altering the operational database: Django 
automatically creates a test database when tests are run and destroys it when the 
tests have completed or failed.  See https://docs.djangoproject.com/en/1.7/topics/testing/overview

To run them: `cd espa-web; . bin/activate; cd web; python ./manage.py test ordering.tests`

## Running
If uWSGI is installed to the system :`cd espa-web; uwsgi -i uwsgi.ini`

If uWSGI is installed to the virtual environment: `cd espa-web; . bin/activate; wsgi -i uwsgi.ini`

You can of course run the built-in django development server for development,
but it is strongly recommended that instead you use uWSGI with the configuration
provided in uwsgi.ini. There are two options for installing uWSGI, inside the virtualenv
or onto the base system.

For ESPA operations, uWSGI is installed to the base system with this project running
inside a uWSGI vassal, which is then managed by an emperor process.

This allows the application to be started without explicitly activate the virtual environment
via bin/activate.

Another option is to install uWSGI into the virtual environment itself via pip. The upside here
is that pip will be more up to date than system package manager repositories.  The downside is 
that the virtual environment will need to be activated before uWSGI is available to be run.
You would also need to made entries in your system process manager (systemd, upstart, etc) to 
start the uWSGI server on boot.
