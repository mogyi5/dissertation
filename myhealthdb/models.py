# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models
from django.contrib.auth.models import User, AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
      (1, 'patient'),
      (2, 'doctor'),
      (3, 'receptionist'),
      (4, 'admin'),
    )

    user_type = models.IntegerField(choices = USER_TYPE_CHOICES, null=True)

    def __str__(self):
        return self.email


class Address(models.Model):
    line1 = models.CharField(max_length=64)
    line2 = models.CharField(max_length=64, null=True, blank=True)
    city = models.CharField(max_length=32)
    postcode = models.CharField(max_length=32)
    country = models.CharField(max_length=32)

    class Meta:
        unique_together = (('postcode', 'line1'),)
        verbose_name_plural = "addresses"

    def __str__(self):
        return self.postcode

class Patient(models.Model):

    SEX  =(
        ('M', 'Male'),
        ('F', 'Female')
    )

    name = models.CharField(max_length=64)
    sex = models.CharField(choices = SEX, max_length=32)
    dob = models.DateField()
    weight = models.DecimalField(max_digits=255, decimal_places=2, blank=True, null=True)
    height = models.IntegerField(blank=True, null=True)
    tel_no = models.CharField(max_length=32, blank=True, null=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True), 
    nhs_no = models.CharField(unique=True, max_length=128, blank=True, null=True)
    baseuser = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)

    # def save(self, *args, **kwargs):
    #     self.baseuser.user_type=1
    #     super(Patient, self).save(*args, **kwargs)

    def __str__(self):
        return self.baseuser.id

class Hospital(models.Model):

    TYPE = (
        ('General Practice', 'General Practice'),
        ('General Hospital', 'General Hospital'),
        ('Specialized Hospital', 'Specialized Hospital')
    )

    COUNTRY = (
        ('United Kingdom', 'United Kingdom'),
        ('Ireland', 'Ireland'),
        ('France', 'France')
    )

    name = models.CharField(max_length=64)
    region = models.CharField(max_length=64)
    address = models.OneToOneField(Address, on_delete=models.PROTECT)
    country = models.CharField(max_length=64, choices = COUNTRY)
    type = models.CharField(max_length=64, choices = TYPE)

    def __str__(self):
        return self.name


class Ward(models.Model):
    name = models.CharField(max_length=64)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    type = models.CharField(max_length=32)
    w_id = models.AutoField(primary_key=True)

    def __str__(self):
        return self.name
        

class Staff(models.Model):

    ROLE = (
        ('Doctor','Doctor'),
        ('Admin', 'Admin'),
    )

    name = models.CharField(max_length=64)
    tel_no = models.CharField(max_length=32, blank=True, null=True)
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True)
    baseuser = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key = True)

    class Meta:
        verbose_name_plural = "staff" 

    def __str__(self):
        return self.baseuser.email

class PatientDoctor(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Staff, on_delete=models.CASCADE)
    primary = models.BooleanField()
    pd_id = models.AutoField(primary_key=True)
    inpatient = models.BooleanField()

    def save(self, *args, **kwargs):   ####watch out for this code######################
        if self.primary:
            try:
                temp = PatientDoctor.objects.get(primary=True)
                if self != temp:
                    temp.primary = False
                    temp.save()
            except PatientDoctor.DoesNotExist:
                pass
        super(PatientDoctor, self).save(*args, **kwargs)

    def __str__(self):
        return self.patient


class Activity(models.Model):

    TYPE = (
	 ('Run','Run'),
	 ('Jog','Jog'),
	 ('Walk','Walk'),
	 ('Cycle','Cycle'),
	 ('Swim','Swim'),
    )

    UNIT = (
	 ('m','m'),
	 ('Km','Km'),
	 ('Mi','Mi'),
    )

    a_id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField()
    calories = models.IntegerField(blank=True, null=True)
    type = models.CharField(choices=TYPE, max_length=32)
    distance = models.IntegerField(blank=True, null=True)
    distance_unit = models.CharField(max_length=32, choices = UNIT, blank=True, null=True )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name_plural = "activities"

    def __str__(self):
        return self.type


class Condition(models.Model):

    TYPE = (
	 ('Allergy','Allergy'),
	 ('Heart Condition','Heart Condition'),
	 ('Blindness','Blindness'),
	 ('Deaf','Deaf'),
    )

    SEVERITY = (
        ('Minor', 'Minor'),
        ('Low', 'Low'),
        ('Moderate','Moderate'),
        ('Very High','Very High'),
        ('Severe', 'Severe'),
    )

    start = models.DateField()
    stop = models.DateField(blank=True, null=True)
    type = models.CharField(max_length= 64,choices = TYPE, blank=True, null=True)
    reaction = models.CharField(max_length=64)
    severity = models.IntegerField(choices = SEVERITY, blank=True, null=True)
    details = models.CharField(max_length=256, blank=True, null=True)
    title = models.CharField(max_length=32)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)


    class Meta:
        unique_together = ('start', 'title', 'patient'),

    def __str__(self):
        return self.type


class Document(models.Model):

    TYPE = (
        ('Discharge Letter', 'Discharge Letter'),
        ('Lab Result', 'Lab Result'),
    )

    name = models.CharField(primary_key=True, max_length=32)
    read = models.BooleanField(default=False)
    file = models.FileField()
    description = models.CharField(max_length=256, blank=True, null=True)
    type = models.CharField(choices = TYPE, max_length=32)

    # class Meta:
    def __str__(self):
        return self.name

class EmergencyContact(models.Model):
    name = models.CharField(max_length=64)
    email = models.CharField(max_length=64, blank=True, null=True)
    phone = models.CharField(primary_key=True, max_length=64)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name


class Event(models.Model):

    TYPE = (
        ('Surgery', 'Surgery'),
        ('Consultation', 'Consultation'),
        ('Imunization','Immunization'),
        ('Emergency', 'Emergency'),
    )

    letter = models.ForeignKey(Document, on_delete=models.SET_NULL, null=True)  #if letter gets deleted doesn't mean that event will
    date_in = models.DateTimeField()
    date_out = models.DateTimeField(blank=True, null=True)
    pd_relation = models.ForeignKey(PatientDoctor, on_delete=models.PROTECT) #unsure about this one
    type = models.CharField(choices=TYPE, max_length=32)
    notes = models.CharField(max_length=256, blank=True, null=True)

    class Meta:
        unique_together = ('date_in', 'pd_relation'),

    def __str__(self):
        return self.type


class Immunization(models.Model):
    TYPE = (
        ('FLU', 'Influenza'),
        ('ZIK', 'Zika Virus')
    )

    date = models.DateField()
    end = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=64,choices=TYPE)
    amount = models.CharField(max_length=32)
    patient = models.ForeignKey(Patient, on_delete = models.CASCADE)

    def __str__(self):
        return self.type

    class Meta:
        unique_together = ('type', 'patient', 'date'),


class Medication(models.Model):
    notes = models.CharField(max_length=256, blank=True, null=True)
    type = models.CharField(max_length=64)
    amount = models.CharField(max_length=16, blank=True, null=True)
    frequency = models.CharField(max_length=64)
    patient = models.ForeignKey(Patient, on_delete= models.CASCADE) 

    class Meta:
        unique_together = ('type', 'patient'),

    def __str__(self):
        return self.type


class PatientEm(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    emcontact = models.ForeignKey(EmergencyContact, on_delete=models.CASCADE) 
    p_id = models.AutoField(primary_key=True)

    def __str__(self):
        return self.emcontact


class Symptom(models.Model):
    name = models.CharField(primary_key=True, max_length=64)

    def __str__(self):
        return self.verbose_name_plural


class SymptomsSet(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    diagnosis = models.CharField(max_length=256, blank=True, null=True)
    date = models.DateTimeField()
    name = models.CharField(max_length=32)
    severity = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.diagnosis

DEFAULT_STAFF_EMAIL = 'default@default.com'
class Task(models.Model):
    deadline = models.DateTimeField(primary_key=True)
    notes = models.CharField(max_length=256)
    complete = models.BooleanField()
    name = models.CharField(max_length=32)
    #set_by = models.ForeignKey(Staff)
    completed_by = models.ForeignKey(Staff, on_delete=models.SET_DEFAULT, default=DEFAULT_STAFF_EMAIL)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('deadline', 'name'),

#################################################################################################################################################

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
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
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