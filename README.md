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

## Change Notes

###### Version 2.9.0 (December 2015)
* added staff only products for evaluation
  * envi-bip format
  * lst
* added staff views for reporting
* updated images
* added extended attribute addition/removal for distributed files as a failsafe to prevent data loss
* enforced maximum size on bounding box for image extents
* clearing note field on products after they leave retry status

###### Version 2.8.15 (November 2015)
* added equal access scheduling 

###### Version 2.8.14 (November 2015)
* restricted L8 surface reflectance based products from November 1st, 2015 onward (day 305)

###### Version 2.8.13 (October 2015)
* updated lsrd image list for index page

###### Version 2.8.12 (October 2015)
* corrected text area size limit on submission page

###### Version 2.8.11 (October 2015)
* upgraded Django to 1.8
* added ordering.tests directory with some simple unit tests
* added psycopg to requirements, now using Postgres in lieu of Mysql
* added exception logging to all rpc.py methods
* rewrote core.py:get_products_to_process to use straight SQL (got queries down to only 1)
* added load_config and dump_config to core.py, allowing configuration bootstrapping
* conventionalized configuration keys minus a couple used by external scripts
* auto_purge policy execution is now part of app instead of external shell script

###### Version 2.8.10 (August 2015)
* updated project to rely on virtualenv for dependencies

###### Version 2.8.9 (August 2015)
* removed google analytics from the site
* replaced the timed rotating file handler for logfiles with standard filehandler.  Logrotate will be used to manage the server logs.

###### Version 2.8.8 (August 2015)
* added a global lock for calls to determine order disposition from rpc.py via memcache.  This is to stop multiple instances of this process from running.  The cache key is set in settings.py and the timeout on this key(lock) is 21 minutes.  If the call succeeds then the lock is removed immediately.
* removed espa_common and rehomed the code under ordering
* added in standard django (python) logging 

###### Version 2.8.7 (August 2015)
* altered queries for checking modis to operate product by product rather than in bulk.  The service calls to lpdaac were taking way too long and causing long running transactions to lock rows.

###### Version 2.8.6 (August 2015)
* added caching to rss feed via urls.py in ordering

###### Version 2.8.5a (July 2015)
* removed items unrelated to the webapp
* retagged as 2.8.5a to allow deployment to differentiate between it and the previous version

###### Version 2.8.5 (July 2015)
* Added additional error condition to network errors 
  * retry on socket timeouts

###### Version 2.8.4 (July 2015)
* Added additional error conditions to the auto error resolver
  * sixs failures now retry
  * additional warp failures result in status unavailable

###### Version 2.8.3 (July 2015)
* Modified RSS feed queries to use raw SQL due to performance overhead with large orders.
* Created separate uwsgi ini configurations for each environment to ease deployment logic.
* Removed deploy_install.sh and replaced with deploy_install.py, which now works with github instead of subversion on Google Projects.
* Updated lsrd_stats.py to work off of separate credentials to support reporting from the historical db.
* Enhanced processing system to support using a local path for output product delivery and code cleanup associated with supporting the local path.
* Modified warping parameters for UTM South to match UTM North with both now using the WGS84 datum.

###### Version 2.8.1 (May 2015)
* Added additional error conditions to the master error handler
* Cosmetic changes for field labels
* Removed inventory restrictions on L8SR TIRS failure scenes

###### Version 2.8.0 (May 2015)

###### Version 2.7.2 (March 4, 2015)
* Added DSWE to ECV section for staff only
* Corrected bugs with validation messages
* UI updates for images on index page

###### Version 2.7.1 (January 6, 2015)
* Added status update retry logic to processing tier.
* Corrected set_product_retry in app tier to include log file.

###### Version 2.7.0 (December 22, 2014)
* Added auto-retry logic.
* Added landsat 8 surface reflectance.
* Added timeout for SUDS ObjectCache.
* Utilizing EE HTTP services for ordering and level 1 download.

###### Version 2.5.0 (August 27, 2014)
* Added console application for staff personnel.
* Added priority to Orders in conjunction with Hadoop Queueing to prevent
* large orders from dominating all compute resources.
* Moved espa schema file to espa-common to prevent network effects from causing processing failures.
* Added select MODIS products as customizable input products.
* Corrected error with invalid checksum generation.
* Multiple bug fixes relating to image reprojection and resampling.
* Added trunk/espa_common to hold shared libs between web and processing.

###### Version 2.4.0 (July 29, 2014)
* Transitioned to binary raster processing for science algorithms.
* Introduced schema constrained xml metadata for all products.
* Format conversion has been introduced.
* Reprojected products now have properly populated metadata entries.

###### Version 2.3.0 (May 30, 2014)
* Added ability to authenticate users against EarthExplorer
* reorganized lta.py, added service clients for RegistrationService
* L1T order submission changed from LTA Massloader to LTA OrderWrapperService
* Added temporary logic to search for user email addresses in both the Django auth User table and the Order email field to support migration of EE auth.
  * Order.email field will be removed with the next release.
* Upgraded to Django 1.6
* Upgraded project structure to be Django 1.6 compliant
* Reorganized the orderservice directory
  * now called 'web'
  * moved contents of 'htdocs' into 'web/static'
  * populated 'web/static' with Django admin static content, eliminating need for softlinks
  * regenerate these with ./manage.py collectstatic

* Modified settings.py to include the static files app and set STATIC_ROOT, STATIC_URL
* Added LOGIN_URL, LOGIN_REDIRECT_URL
* Added URL_FOR() lambda function as service locator function
  * was previously implemented in lta.py, multiple modules now need this and its a critical dependency 
* Added ESPA_DEBUG flag to settings.py
  * looks for ESPA_DEBUG = TRUE in environment variables, enables DEBUG and TEMPLATE_DEBUG
* Moved all configuration items to settings.py
  * configurable items can be set in espa-uwsgi.ini or as environment variables
  * private key & database credentials must be provided on the local filesystem in ~/.cfgno
* Removed the /media mapping in espa-uwsgi.ini as it is no longer necessary (merged into /static mapping)
* django.wsgi removed in favor of django generated wsgi.py
* Deleted scene_cache.py from the espa/ codebase
  * Moved the scene cache replacement from trunk/prototype/new_scene_cache to trunk/scenecache.
* Moved all Order & Scene related operations to the models.Order and models.Scene classes as either class or static methods
* Removed all partially hardcoded urls from template and view code, replaced with named urls, {% url %}, {% static %} and reverse() tags
* Moved all cross-application functionality into espa_web
* Added espa_web/context_processors.py to include needed variables in templates
  * must include in settings.py TEMPLATE_CONTEXT_PROCESSORS
* Added espa_web/auth_backends.py for EE authentication 
  * Django auth system plugin
  * must include in settings.py AUTHENTICATION_BACKENDS

###### Version 2.2.5 (March 11, 2014)
* Made change to support variable cloud pixel threshold for calls to cfmask.

###### Version 2.2.4 (December 20, 2013)
* Bug fix to parse_hdf_subdatasets() in cdr_ecv.py to correct reprojection failures.

###### Version 2.2.3
* Altered cdr_ecv to use straight FTP rather than SCP (performance)

###### Version 2.2.2
* Added SCA & SWE to internal ordering
* Corrected unchecked reprojection errors
* Corrected Bulk Ordering Navigation
* Fail job submission if no products selected
* Added MSAVI to spectral indices
* Merged all vegetation indices to a single raster
* Removed standalone CFMask option
* Removed solr index generation option
* Corrected cross browser rendering issues

###### Version 2.2.1
* Fixed bug reprojecting spectral indices
* Fixed bug reprojecting cfmask
* Modified reprojected filename extensions to '.tif'
* Defaulted pixel size to 30 meters or dd equivalent when necessary.
* Corrected Albers subsetting failures.
* Modified code to properly clean up HDFs when reprojecting/reformatting to GeoTiff
* Optimized calls to warp outputs in the cdr_ecv.
* Added first set of prototype system level tests for cdr_ecv.py

###### Version 2.2.0
* Added code to perform reprojection.
* Added code to perform framing.
* Added code to perform subsetting.

###### Version 2.1.6
* Reorganized the codebase to accomodate LPVS code.
* Implemented a standardized logging format.
* Added webpages for marketing.

###### Version 2.1.5
* Added a lockfile to the scene_cache update to prevent multiple processes from running, which causes contention

###### Version 2.1.4
* Bug fix for duplicate orders from EE.  Modified core.py load_orders_from_ee() to look for an order + scene in the db before attempting to add a new one

###### Version 2.1.3
* Fix to clear logs upon non-error status update.
* Initial version of api.py added.
* Integration for SI 1.1.2, cfmask 1.1.1, ledaps 1.3.0, cfmask_append 1.0.1, swe 1.0.0
* Updated code to interact with online cache over private 10Gig network
* Added load balancing code mapper.py for contacting the online cache

###### Version 2.1.2
* Updates for new cfmask and appending cfmask to sr outputs.
* Multiple bug fixes related to UI css files when viewed of https

###### Version 2.1.1
* Update internal email verbage to remove "Surface Reflectance"
* Bug fixes for LTA integration when processing mixed orders
* Fixed product file names
* Corrected bug where espa user interface wouldn't accept a Glovis scenelist
* Added all available spectral indices to espa_internal
* Integrated cfmask 1.0.4
* Integrated updated Spectral Indices

###### Version 2.1
* Updated web code to verify submitted scenes against the inventory before accepting them.
* Updated web code to pull orders from EE on demand for surface reflectance only.

###### Version 2.0.4
* Update espa to work with new ledaps and cfmask
* Corrected issue with bad tarballs being distributed.
* Generated cksum files and distribute those with the product.

###### Version 2.0.3
* Updated espa to work with ledaps 1.2 & cfmask 1.0.1
* Added ability for all users to select product options.
* Added ability to order cfmask for espa_internal and espa_admin
* Removed seperate source file distribution (can be selected as an option)

###### Version 2.0.2
* Fixed solr generation to account for landsat metadata field name changes
* Changed espa TRAM ordering priority
* Tested setting ESPA work directory to "." or cwd()

###### Version 2.0.1
* Added espa_internal for evaluation.

###### Version 2.0.0
* Modified architecture to remove the Chain of Command structure from processing.
* Modified espa to work with ledaps 1.1.2.
* Added ability for end users to select which products they want in their delivery (admin acct only at this time.)
* Added mapper.py and removed any external calls from espa.py except for scp calls to obtain data.  Mapper.py handles all status notifications to the espa tracking node now.

###### Version 1.3.8
* Updated espa to work with ledaps 1.1.1.

###### Version 1.3.7
* Updated espa to work with ledaps 1.1.0.  Added scene_cache.py to speed up scene submission.
* Multiple bugfixes and cosmetic website/email changes.

###### Version 1.3.5
* Updated 'lndpm' binary to work with new Landsat metdata
* Corrected metadata file lookup to account for Landsat's metadata format changes.

###### Version 1.3.4
* Corrections to reprojection code in espacollection.py when creating browse images.
 
###### Version 1.3.3
* Modifications to the NDVI code to release memory more quickly, reduce memory footprint.

###### Version 1.3.2
* Correction to the solr index to be semicolon seperated

###### Version 1.3.1
* Bug fixes for NDVI and CleanupDirs

###### Version 1.3
* Updated LEDAPS to the latest version from November 2011.  Added ability to generate NDVI for output products
* Multiple additions to collection processing to create browse and solr index.

###### Version 1.2
* Replaced Python's tar and untar commands in espa.py with the native operating system commands.
  * Prior to this there were intermittent corrupt archives making it into the distribution node.

###### Version 1.1
* Added RSS Status capability to ordering interface

###### Version 1.0
* First major stable version of ESPA released that will process Landsat L1T's to Surface Reflectance
