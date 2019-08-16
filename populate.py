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
    patient1 = CustomUser.objects.create_user(username='patient',email='patient@patient.com',password='myhealthdb', user_type='1' )
    patient2 = CustomUser.objects.create_user(username='patient2',email='patient2@patient2.com',password='myhealthdb', user_type='1' )
    patient3 = CustomUser.objects.create_user(username='patient3',email='patient3@patient3.com',password='myhealthdb', user_type='1' )
    doctor1 = CustomUser.objects.create_user(username='doctor',email='doctor@doctor.com',password='myhealthdb', user_type = '2' )
    doctor2 = CustomUser.objects.create_user(username='doctor2',email='doctor2@doctor2.com',password='myhealthdb', user_type = '2' )
    doctor3 = CustomUser.objects.create_user(username='doctor3',email='doctor3@doctor3.com',password='myhealthdb', user_type = '2' )
    receptionist1 = CustomUser.objects.create_user(username='receptionist1',email='receptionist1@receptionist1.com',password='myhealthdb', user_type = '3' )
    receptionist2 = CustomUser.objects.create_user(username='receptionist2',email='receptionist2@receptionist2.com',password='myhealthdb', user_type = '3' )
    itguy = CustomUser.objects.create_user(username='itguy',email='it@it.com',password='myhealthdb', user_type = '4' )
# populating the patients also
    Profiles = {
    "patient@patient.com":{'firstname':'pat', 'lastname':'pot',"sex": "Female", "dob": "2002-02-02", "tel_no": "111111111111"}, #, "address":"UK, Birmingham"}, #"ad_line1":"my first line", "ad_city":"glasgow", "ad_postcode":"g22 opp", "ad_country":"uk"},
    "patient2@patient2.com":{'firstname':'bot', 'lastname':'bat',"sex": "Male", "dob": "2003-03-03", "tel_no": "2222222222222"},# "address":"UK, London"},# "ad_line1":"hello hello", "ad_city":"edinburgh", "ad_postcode":"ginaaa", "ad_country":"england"},    
    "patient3@patient3.com":{'firstname':'yoyo', 'lastname':'whatsup',"sex": "Female", "dob": "2004-04-04", "tel_no": "333333333333"},# "address":"UK, Glasgow, Rosevale 23"},#  "ad_line1":"i am groot", "ad_city":"wales", "ad_postcode":"binary", "ad_country":"spain"},
    }

    for p, p_data in Profiles.items():
        add_patient(CustomUser.objects.get(email = p),p_data['firstname'],p_data['lastname'], p_data["sex"], p_data["dob"], p_data["tel_no"])#, p_data['address'])  #p_data["ad_line1"], p_data["ad_city"],p_data["ad_postcode"], p_data["ad_country"])

# populating the hospitals also
    Hospitals = {
    'hospital1':{'name':'hospital1', 'type':'General Practice', "address":"(55.865033041338116,-4.185080086179028)"},   #, "ad_city":"inverness", "ad_postcode":"iv22 747", "ad_country":"uk"},
    'hospital2':{'name':'hospital2', 'type':'General Hospital', "address":"(55.8875669717464,-4.080023323483715)"}, #, "ad_city":"aberdeen", "ad_postcode":"ab56566", "ad_country":"greenland"},
    }

    for p, p_data in Hospitals.items():
        add_hospital(p_data['name'], p_data["type"], p_data['address'])#, p_data["address"])#, p_data["ad_city"],p_data["ad_postcode"], p_data["ad_country"]) 

# populating the wards also
    Wards = {
    'ward':{'name':'ward', 'type':'Cancer'},
    'ward2':{'name':'ward2', 'type':'Pediatry'},
    'ward3':{'name':'ward3', 'type':'Genius'},
    }

    for p, p_data in Wards.items():
        add_ward(p_data['name'], Hospital.objects.get(name = 'hospital1'), p_data["type"])


# populating the staff also
    Staff = {
    "doctor@doctor.com":{'firstname':'dic', 'lastname':'doc',"tel_no": "222222222222", "ward": "ward"},
    "doctor2@doctor2.com":{'firstname':'derek', 'lastname':'doo',"tel_no": "1324", "ward": "ward"},
    "doctor3@doctor3.com":{'firstname':'drunk', 'lastname':'yoohoo',"tel_no": "07479509090",  "ward": "ward2"},
    "receptionist1@receptionist1.com":{'firstname':'ella', 'lastname':'b',"tel_no": "849002380",  "ward": "ward2"},
    "receptionist2@receptionist2.com":{'firstname':'recept', 'lastname':'ionist',"tel_no": "7743",  "ward": "ward"},
    "it@it.com":{'firstname':'itguy', 'lastname':'itguy',"tel_no": "7789798743",  "ward": "ward"},
    }

    for p, p_data in Staff.items():
        add_staff(CustomUser.objects.get(email = p),p_data['firstname'],p_data['lastname'], p_data["tel_no"], Ward.objects.get(name = p_data['ward']))

## making a superuser
def create_super_user(username, email, password):
    try:
        u = CustomUser.objects.create_superuser(username, email, password)
        return u
    except IntegrityError:
        pass


# make profiles for the patients
def add_patient(baseuser, firstname, lastname, sex, dob, tel_no):#, address):#line1, city, postcode, country):
    p = Patient.objects.get_or_create(baseuser = baseuser, first_name=firstname, last_name=lastname, sex=sex, dob=dob, tel_no=tel_no)[0]#, address=address)[0] #ad_line1=line1, ad_city=city, ad_postcode=postcode, ad_country=country)[0]
    return p

def add_staff(baseuser, firstname, lastname, tel_no, ward):
    p = Staff.objects.get_or_create(baseuser = baseuser, first_name=firstname, last_name=lastname, tel_no=tel_no, ward=ward)[0]
    return p

def add_hospital(name, type, address): #ad_line1,ad_city, ad_postcode, ad_country):
    p = Hospital.objects.get_or_create(name=name, type=type)[0]#, address=address)[0] #ad_line1=ad_line1, ad_city=ad_city, ad_postcode=ad_postcode, ad_country=ad_country)
    return p

def add_ward(name, hospital, type):
    p = Ward.objects.get_or_create(name=name, hospital = hospital, type=type)
    return p

if __name__=='__main__':
	print("Starting population script...")
populate()