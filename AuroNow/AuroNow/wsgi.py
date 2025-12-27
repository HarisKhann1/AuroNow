# """
# WSGI config for AuroNow project.

# It exposes the WSGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
# """

# import os

# from django.core.wsgi import get_wsgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AuroNow.settings')

# application = get_wsgi_application()

"""
WSGI config for AuroNow project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from dotenv import load_dotenv

# Load environment variables from the .env file
project_folder = os.path.expanduser('/home/AuroNow/AuroNow')  # path to your .env
load_dotenv(os.path.join(project_folder, '.env'))

# Set default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AuroNow.settings')

# Start the application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

