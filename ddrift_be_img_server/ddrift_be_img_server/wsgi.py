"""
WSGI config for ddrift_be_img_server project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import os
os.environ["DJANGO_SETTINGS_MODULE"] = "ddrift_be_img_server.settings"

import sys
base = os.path.dirname(os.path.dirname(__file__))
base_parent = os.path.dirname(base)
if base not in sys.path:
  sys.path.insert(0, base)
if base_parent not in sys.path:
  sys.path.insert(0, base_parent)


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
