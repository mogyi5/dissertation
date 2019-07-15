import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myhealthdb_project.settings')

import django
django.setup()
from django.contrib.auth.models import User
from django.db import IntegrityError
from myhealthdb.models import CustomUser, Patient, Staff, Hospital, Ward


def populate():

## making a superuser
    username = '2378361s@student.gla.ac.uk '
    email = '2378361s@student.gla.ac.uk'
    password = 'myhealthdb'

    super = create_super_user(username, email, password)

# making some new users for fun
    patient = CustomUser.objects.create_user(username='patient',email='patient@patient.com',password='myhealthdb', user_type='1' )
    doctor = CustomUser.objects.create_user(username='doctor',email='doctor@doctor.com',password='myhealthdb', user_type = '2' )

# populating the patients also
    Profiles1 = {
    "patient@patient.com":{'firstname':'pat', 'lastname':'pot',"sex": "Female", "dob": "2002-02-02", "tel_no": "111111111111", "ad_line1":"my first line", "ad_city":"glasgow", "ad_postcode":"g22 opp", "ad_country":"uk"},
    }

    for p, p_data in Profiles1.items():
        add_patient(CustomUser.objects.get(email = p),p_data['firstname'],p_data['lastname'], p_data["sex"], p_data["dob"], p_data["tel_no"], p_data["ad_line1"], p_data["ad_city"],p_data["ad_postcode"], p_data["ad_country"])

# populating the staff also
    Profiles2 = {
    "doctor@doctor.com":{'firstname':'dic', 'lastname':'doc',"tel_no": "222222222222"},
    }

    for p, p_data in Profiles2.items():
        add_staff(CustomUser.objects.get(email = p),p_data['firstname'],p_data['lastname'], p_data["tel_no"])

# populating the hospitals also
    Hospitals = {
    'hospital1':{'name':'hospital1', 'region':'highlands', 'type':'General Practice', "ad_line1":"first", "ad_city":"inverness", "ad_postcode":"iv22 747", "ad_country":"uk"},
    }

    for p, p_data in Hospitals.items():
        add_hospital(p_data['name'],p_data['region'], p_data["type"], p_data["ad_line1"], p_data["ad_city"],p_data["ad_postcode"], p_data["ad_country"]) 

# populating the wards also
    Wards = {
    'ward':{'name':'ward', 'type':'General Practice'},
    }

    for p, p_data in Wards.items():
        add_ward(p_data['name'], Hospital.objects.get(name = 'hospital1'), p_data["type"])

## making a superuser
def create_super_user(username, email, password):
    try:
        u = CustomUser.objects.create_superuser(username, email, password)
        return u
    except IntegrityError:
        pass


# make profiles for the patients
def add_patient(baseuser, firstname, lastname, sex, dob, tel_no, line1, city, postcode, country):
    p = Patient.objects.get_or_create(baseuser = baseuser, first_name=firstname, last_name=lastname, sex=sex, dob=dob, tel_no=tel_no, ad_line1=line1, ad_city=city, ad_postcode=postcode, ad_country=country)[0]
    return p

def add_staff(baseuser, firstname, lastname, tel_no):
    p = Staff.objects.get_or_create(baseuser = baseuser, first_name=firstname, last_name=lastname, tel_no=tel_no)[0]
    return p

def add_hospital(name, region, type, ad_line1,ad_city, ad_postcode, ad_country):
    p = Hospital.objects.get_or_create(name=name, region=region, type=type, ad_line1=ad_line1, ad_city=ad_city, ad_postcode=ad_postcode, ad_country=ad_country)
    return p

def add_ward(name, hospital, type):
    p = Ward.objects.get_or_create(name=name, hospital = hospital, type=type)
    return p

if __name__=='__main__':
	print("Starting YumYum population script...")
populate()