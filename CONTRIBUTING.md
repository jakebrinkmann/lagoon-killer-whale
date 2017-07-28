## Installation
* Clone this project: `git clone https://github.com/USGS-EROS/espa-web.git espa-web`
* Satisfy system dependencies listed in [requirements.txt](/setup/requirements.txt)
  * Create a virtualenv: `cd espa-web; virtualenv .`
  * Install dependencies: `. bin/activate; pip install -r requirements.txt`
* Set `ESPA_LOG_DIR` env var.  Defaults to `/var/log/uwsgi/`
* Set `ESPAWEB_SETTINGS` env var to point to db values (defaults to `~/.cfgnfo`)

##### Required API config in ESPAWEB_SETTINGS
```
DEBUG = False                                                                      
SECRET_KEY='superS3cre+'                      
```

## Testing
Unit tests are included for the application to ensure system integrity. 
To run them: `cd espa-web; . bin/activate; nose2 --verbose --fail-fast`

**Note**: The tests currently require an active Memcache session (localhost).

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
