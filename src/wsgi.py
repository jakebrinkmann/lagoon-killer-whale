"""
WSGI config for espa_web flask project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""
from app import app

if __name__ == "__main__":
    app.run()