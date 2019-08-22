from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django_random_queryset import RandomManager
from django.utils.text import slugify
from myhealthdb.modelchoices import *
from django.db.models.signals import post_delete
from django.dispatch import receiver
from geopy.geocoders import Nominatim
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re
import os
from phonenumber_field.modelfields import PhoneNumberField

#-------------------------------validators------------------------------

#only allow pdf files for the file extension
def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf',]
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')

#online allow 10digit long numbers for the nhs number
def nhs_validator(value):
    reg = re.compile('^[0-9 ]*$')
    if (len(value) != 10 or not reg.match(value)):
        raise ValidationError('Number should be numberic and 10 digits long')

#only allow text and spaces
def text_validator(value):
    reg = re.compile('^[a-zA-Z ]*$')
    if not (reg.match(value)):
        raise ValidationError('Field should be alphabetical')

#only allow positive numbers
def number_positive_validator(value):
    if (value < 0):
        raise ValidationError('%s should not be negative' % value)

#------------------------------models-------------------------------------

#the base/parent user model which patient and staff extend
class CustomUser(AbstractUser):

    #this determines whether a user is a patient/staff, privileges and access are based on this
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES, null=True)

    def __str__(self):
        return self.email


class Patient(models.Model):

    #must have a name
    first_name = models.CharField(max_length=32, validators=[text_validator,])
    last_name = models.CharField(max_length=32, validators=[text_validator,])

    #basic details like sex, dob and tel_no, optional nhs_no
    sex = models.CharField(choices=SEX, max_length=32)
    dob = models.DateField()
    tel_no = PhoneNumberField(blank=True, null=True)
    nhs_no = models.CharField(max_length=128, blank=True, null=True, validators=[nhs_validator,])

    #the parent user which is one-to-one with this patient
    baseuser = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='patient')

    #address related things, flat_no for more clarification, address only inputs street address
    flat_no = models.CharField(max_length=32, null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)

    #if deleted, delete customuser too
    def delete(self, *args, **kwargs):
        super(Patient, self).delete(*args, **kwargs)
        base = CustomUser.objects.get(id=self.baseuser.id)
        base.delete()

    #when called, return this
    def __str__(self):
        return self.first_name + " " + self.last_name


class Hospital(models.Model):

    objects = RandomManager()
    name = models.CharField(max_length=64, validators=[text_validator,])

    #the type can be like private practice, general hospital, specialised hospital
    type = models.CharField(max_length=64, choices=HOSPITAL_TYPE)
    address = models.CharField(max_length=256)

    #taking_patients must be true for patients to be able to register at the hospital
    taking_patients = models.BooleanField(default=True)

    #delete the hospital's group on delete
    def delete(self, *args, **kwargs):
        super(Hospital, self).delete(*args, **kwargs)
        group = Group.objects.get(name=self.name)
        group.delete()

    #make a group for the hospital on save
    def save(self, *args, **kwargs):
        super(Hospital, self).save(*args, **kwargs)
        group, created = Group.objects.get_or_create(name=self.name)

    def __str__(self):
        return self.name


class Ward(models.Model):
    name = models.CharField(max_length=64, validators=[text_validator,])
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)

    #type of the ward may be cancer ward or some such 
    type = models.CharField(max_length=32)

    #delete the ward's group on delete
    def delete(self, *args, **kwargs):
        super(Ward, self).delete(*args, **kwargs)
        group = Group.objects.get(name=self.name)
        group.delete()

    #create a group for the ward on save
    def save(self, *args, **kwargs):
        super(Ward, self).save(*args, **kwargs)
        group, created = Group.objects.get_or_create(name=self.name)

    def __str__(self):
        return self.name


class Staff(models.Model):

    first_name = models.CharField(max_length=32, validators=[text_validator,])
    last_name = models.CharField(max_length=32, validators=[text_validator,])
    tel_no = PhoneNumberField(blank=True, null=True)

    #the ward in which the staff works, may have only one
    ward = models.ForeignKey(
        Ward, on_delete=models.SET_NULL, blank=True, null=True, related_name='current_ward')

    #the room of the staff
    room = models.CharField(max_length=32, blank=True, null=True)

    #the parent baseuser of the staff, one-to-one relationship
    baseuser = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='doctor')

    #on save, add the staff to the groups of its ward and hospital
    def save(self, *args, **kwargs):

        super(Staff, self).save(*args, **kwargs)

        if self.ward:
            group = Group.objects.get(name=self.ward.name)
            group2 = Group.objects.get(name=self.ward.hospital.name)
            group.members.add(self)
            group2.members.add(self)

            mygroups = Group.objects.filter(members=self)

            #if there are some man-made groups which are not wards or hospitals, get rid of them and only keep the automatic ones.
            if len(mygroups) > 2:
                for i in range(0, len(mygroups)):
                    if ((mygroups[i].name == self.ward.name) or (mygroups[i].name == self.ward.hospital.name)):
                        pass
                    else:
                        mygroups[i].members.remove(self)

    #the plural of staff is staff
    class Meta:
        verbose_name_plural = "staff"

    def __str__(self):
        return self.baseuser.email


DEFAULT_STAFF_ID = 0


class Group(models.Model):

    name = models.CharField(max_length=128)

    #a group can have many members, a person may be in many groups
    members = models.ManyToManyField(Staff, blank=True)
    
    #the admin that created the group, may be noone if its automatic
    ad = models.ForeignKey(Staff, on_delete=models.SET_NULL,
                           related_name='admin', blank=True, null=True)

    #a description for the group
    description = models.CharField(max_length=256, blank=True, null=True)

    #an automatic slug for the group
    slug = models.SlugField(blank=True)

    #automatic is 0, person created is 1
    type = models.BooleanField(default=False)

    #on save, create the slug
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Group, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

#the relationship between a patient and hospital
class PatientHospital(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='patient')
    hospital = models.ForeignKey(
        Hospital, on_delete=models.CASCADE, related_name='hospital')

    #relationship (registration) must be confirmed by receptionist. status = false, but after confirmation it's true
    status = models.BooleanField(default=False)
    
    #is the patient an inpatient? yes or no
    inpatient = models.BooleanField(default=False)

    #one hospital and patient can only have one relaionship
    class Meta:
        unique_together = ('patient', 'hospital')

    def __str__(self):
        return self.hospital.name + ", " + self.patient.first_name + " " + self.patient.last_name


#condition as in illness
class Condition(models.Model):

    #start and stop dates of the condition, not compulsory
    start = models.DateField()
    stop = models.DateField(blank=True, null=True)

    type = models.CharField(
        max_length=64, choices=CONDITION_TYPE, blank=True, null=True)

    #a description of the reaction, such as an allergy
    reaction = models.CharField(max_length=64)
    severity = models.CharField(
        max_length=32, choices=SEVERITY, blank=True, null=True)

    #could add further details
    details = models.CharField(max_length=256, blank=True, null=True)
    title = models.CharField(max_length=32)

    #who's condition is it
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    #was it added by a doctor or patient?
    added_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True)

    class Meta:
        unique_together = ('start', 'title', 'patient'),

    def __str__(self):
        return self.title


class Document(models.Model):

    name = models.CharField(max_length=32)

    #the pdf_file which is uploaded and stored
    pdf_file = models.FileField(upload_to='documents', blank=False, validators=[validate_file_extension,])

    #may describe the document
    description = models.CharField(max_length=256, blank=True, null=True)
    type = models.CharField(choices=DOC_TYPE, max_length=32)

    #the patient this document concerns
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, blank=True)

    #added by staff or patient?
    added_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True)

    # class Meta:
    def __str__(self):
        return self.name


#a signal, delete the file with the document object
@receiver(post_delete, sender=Document)
def submission_delete(sender, instance, **kwargs):
    instance.pdf_file.delete(False)

#event is an interaction between staff and patients, like an appointment or surgery
class Event(models.Model):

    title = models.CharField(max_length=32)

    #datetime of the event
    date_in = models.DateTimeField()

    #the patienthospital relation which makes this happen
    pd_relation = models.ForeignKey(
        PatientHospital, on_delete=models.CASCADE, related_name='reversepd') 
    type = models.CharField(choices=EVENT_TYPE, max_length=32)
    notes = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        return self.title

#shift is a work shift for staff
class Shift(models.Model):

    #day of work 
    date = models.DateField()

    #start and end times 
    start = models.TimeField()
    end = models.TimeField()

    #which staff does this concern
    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name='staff')

    def __str__(self):
        return str(self.start.strftime("%H:%M")) + '-' + str(self.end.strftime("%H:%M"))

#immunization like an injection
class Immunization(models.Model):

    #date administered
    date = models.DateField()
    
    #valid until
    end = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=64, choices=IMM_TYPE)

    #milligrams or dosage, however nurses measure it
    amount = models.CharField(max_length=32)

    #who was it administered to?
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    #who administered it?
    added_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.type

    class Meta:
        unique_together = ('type', 'patient', 'date'),


class Medication(models.Model):
    notes = models.CharField(max_length=256, blank=True, null=True)

    #not required, could be any kind of medicine or over the counter ailment.
    type = models.CharField(max_length=64)

    #eg. 1 pill
    amount = models.CharField(max_length=16, blank=True, null=True)

    #eq 2x a day
    frequency = models.CharField(max_length=64)

    #who is taking the medication
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    #when did it start taking and when was it finished?
    start = models.DateField(blank=True, null=True)
    finish = models.DateField(blank=True, null=True)

    #who prescribed it?
    added_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True)

    def __str__(self):
        return self.type

#emergency contacts for a patient
class PatientEm(models.Model):

    #the patient whose emergency contacts these are
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='em_pat')

    #contact details
    name = models.CharField(max_length=64)
    email = models.CharField(max_length=64, blank=True, null=True)
    phone1 = PhoneNumberField()
    phone2 = PhoneNumberField(blank=True, null=True)
    p_id = models.AutoField(primary_key=True)

    def __str__(self):
        return self.name


DEFAULT_STAFF_EMAIL = 'default@default.com'

#tasks for staff
class Task(models.Model):
    #due by
    deadline = models.DateTimeField()

    #any other details
    notes = models.CharField(max_length=256, blank=True, null=True)

    #is it done?
    complete = models.BooleanField(default=False)
    name = models.CharField(max_length=20)

    #who set the task?
    set_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, null=True, related_name='setter')
    
    #who should complete it? can be many people
    complete_by = models.ManyToManyField(
        Staff, default=DEFAULT_STAFF_EMAIL, related_name='doer')

    #when was it completed?
    completion_date = models.DateTimeField(null=True, blank=True)

    #who completed it?
    actually_completed = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, blank=True, null=True, related_name='completer')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('deadline', 'completion_date')

#vital like heart rate, weight, height measurements
class Vital(models.Model):

    #current choices are height and weight
    type = models.CharField(max_length=32, choices=VITALTYPE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    #measurements are automatically added now
    date = models.DateField(auto_now=True)
    
    #the actual number value of the measurement
    value = models.DecimalField(decimal_places = 2, max_digits=5, validators=[number_positive_validator,])

    def __str__(self):
        return str(self.patient) + " "+ self.type + " " + str(self.value) 

    class Meta:
        ordering = ('date',)


#----------------------------------MODELS REQUIRED BY POSTGRES, AUTOMATICALLY GENERATED--------------------------------------#


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey(
        'DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
