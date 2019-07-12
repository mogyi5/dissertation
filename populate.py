import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhealthdb_project.settings')

import django
django.setup()
from django.contrib.auth.models import User
from django.db import IntegrityError
from myhealthdb.models import CustomUser


def populate():

## making a superuser
    username = '2378361s@student.gla.ac.uk '
    email = '2378361s@student.gla.ac.uk'
    password = 'myhealthdb'

    super = create_super_user(username, email, password)

## making a superuser
def create_super_user(username, email, password):
    try:
        u = CustomUser.objects.create_superuser(username, email, password)
        return u
    except IntegrityError:
        pass


if __name__=='__main__':
	print("Starting YumYum population script...")
populate()