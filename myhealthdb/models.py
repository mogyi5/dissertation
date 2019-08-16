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
from phonenumber_field.modelfields import PhoneNumberField


def nhs_validator(value):
    reg = re.compile('^[0-9]*$')
    #matches = reg.match(value)
    if (len(value) != 10 or not reg.match(value)):
        raise ValidationError('Number should be numberic and 10 digits long')

def text_validator(value):
    reg = re.compile('^[a-zA-Z]*$')
    #matches = reg.match(value)
    if (not reg.match(value)):
        raise ValidationError('Field should be alphabetical')


def number_positive_validator(value):
    if (value < 0):
        raise ValidationError('%s should not be negative' % value)


class CustomUser(AbstractUser):

    user_type = models.IntegerField(choices=USER_TYPE_CHOICES, null=True)

    def __str__(self):
        return self.email


class Patient(models.Model):

    first_name = models.CharField(max_length=32, validators=[text_validator,])
    last_name = models.CharField(max_length=32, validators=[text_validator,])
    sex = models.CharField(choices=SEX, max_length=32)
    dob = models.DateField()
    tel_no = PhoneNumberField(blank=True, null=True)
    nhs_no = models.CharField(max_length=128, blank=True, null=True, validators=[nhs_validator,])
    baseuser = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='patient')
    flat_no = models.CharField(max_length=32, null=True, blank=True)
    address = models.CharField(max_length=256, null=True, blank=True)

    def delete(self, *args, **kwargs):
        super(Patient, self).delete(*args, **kwargs)
        base = CustomUser.objects.get(id=self.baseuser.id)
        base.delete()

    def __str__(self):
        return self.baseuser.email


class Hospital(models.Model):

    objects = RandomManager()

    name = models.CharField(max_length=64, validators=[text_validator,])
    #region = models.CharField(max_length=64)
    # address = models.OneToOneField(Address, on_delete=models.PROTECT)
    type = models.CharField(max_length=64, choices=HOSPITAL_TYPE)
    address = models.CharField(max_length=256)
    taking_patients = models.BooleanField(default=True)
    # ad_line2 = models.CharField(max_length=64, null=True, blank=True)
    # ad_city = models.CharField(max_length=32)
    # ad_postcode = models.CharField(max_length=32)
    # ad_country = models.CharField(max_length=32)

    def delete(self, *args, **kwargs):
        super(Hospital, self).delete(*args, **kwargs)
        group = Group.objects.get(name=self.name)
        group.delete()

    # make a group for the hospital on save
    def save(self, *args, **kwargs):
        super(Hospital, self).save(*args, **kwargs)
        group, created = Group.objects.get_or_create(name=self.name)

    def __str__(self):
        return self.name


class Ward(models.Model):
    name = models.CharField(max_length=64, validators=[text_validator,])
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    type = models.CharField(max_length=32)
    # taking_new_pat = models.BooleanField(default=False)
    # w_id = models.AutoField(primary_key=True)

    def delete(self, *args, **kwargs):
        super(Ward, self).delete(*args, **kwargs)
        group = Group.objects.get(name=self.name)
        group.delete()

    def save(self, *args, **kwargs):
        super(Ward, self).save(*args, **kwargs)
        group, created = Group.objects.get_or_create(name=self.name)

    def __str__(self):
        return self.name


class Staff(models.Model):

    first_name = models.CharField(max_length=32, validators=[text_validator,])
    last_name = models.CharField(max_length=32, validators=[text_validator,])
    tel_no = PhoneNumberField(blank=True, null=True)
    ward = models.ForeignKey(
        Ward, on_delete=models.SET_NULL, blank=True, null=True, related_name='current_ward')
    room = models.CharField(max_length=32, blank=True, null=True)
    baseuser = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, primary_key=True, related_name='doctor')

    def save(self, *args, **kwargs):

        super(Staff, self).save(*args, **kwargs)

        group = Group.objects.get(name=self.ward.name)
        group2 = Group.objects.get(name=self.ward.hospital.name)
        group.members.add(self)
        group2.members.add(self)

        mygroups = Group.objects.filter(members=self)

        if len(mygroups) > 2:
            for i in range(0, len(mygroups)):
                if ((mygroups[i].name == self.ward.name) or (mygroups[i].name == self.ward.hospital.name)):
                    pass
                else:
                    mygroups[i].members.remove(self)

    class Meta:
        verbose_name_plural = "staff"

    def __str__(self):
        return self.baseuser.email


DEFAULT_STAFF_ID = 0


class Group(models.Model):
    name = models.CharField(max_length=128)
    members = models.ManyToManyField(Staff, blank=True)
    ad = models.ForeignKey(Staff, on_delete=models.SET_NULL,
                           related_name='admin', blank=True, null=True)  # maybe not needed
    description = models.CharField(max_length=256, blank=True, null=True)
    slug = models.SlugField(blank=True)

    # automatic is 0, person created is 1
    type = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Group, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class PatientHospital(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='patient')
    hospital = models.ForeignKey(
        Hospital, on_delete=models.CASCADE, related_name='hospital')
    status = models.BooleanField(default=False)
    inpatient = models.BooleanField(default=False)

    class Meta:
        unique_together = ('patient', 'hospital')

    def __str__(self):
        return self.patient.first_name + '' + self.hospital.name


class Activity(models.Model):

    a_id = models.AutoField(primary_key=True)
    timestamp = models.DateTimeField()
    calories = models.IntegerField(blank=True, null=True)
    type = models.CharField(choices=ACTIVITY_TYPE, max_length=32)
    distance = models.IntegerField(blank=True, null=True)
    distance_unit = models.CharField(
        max_length=32, choices=UNIT, blank=True, null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True)

    class Meta:
        verbose_name_plural = "activities"

    def __str__(self):
        return self.type


class Condition(models.Model):

    start = models.DateField()
    stop = models.DateField(blank=True, null=True)
    type = models.CharField(
        max_length=64, choices=CONDITION_TYPE, blank=True, null=True)
    reaction = models.CharField(max_length=64)
    severity = models.CharField(
        max_length=32, choices=SEVERITY, blank=True, null=True)
    details = models.CharField(max_length=256, blank=True, null=True)
    title = models.CharField(max_length=32)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('start', 'title', 'patient'),

    def __str__(self):
        return self.title


class Document(models.Model):

    name = models.CharField(max_length=32)
    read = models.BooleanField(default=False, blank=True, null=True)
    file = models.FileField(upload_to='documents', blank=False)
    description = models.CharField(max_length=256, blank=True, null=True)
    type = models.CharField(choices=DOC_TYPE, max_length=32)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, blank=True, null=True)

    # class Meta:
    def __str__(self):
        return self.name


@receiver(post_delete, sender=Document)
def submission_delete(sender, instance, **kwargs):
    instance.file.delete(False)


class Event(models.Model):

    title = models.CharField(max_length=32)
    date_in = models.DateTimeField()
    pd_relation = models.ForeignKey(
        PatientHospital, on_delete=models.CASCADE, related_name='reversepd')  # unsure about this one
    type = models.CharField(choices=EVENT_TYPE, max_length=32)
    notes = models.CharField(max_length=256, blank=True, null=True)

    # class Meta:
    #     unique_together = ('date_in', 'pd_relation'),

    def __str__(self):
        return self.title


class Shift(models.Model):
    date = models.DateField()
    start = models.TimeField()
    end = models.TimeField()
    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name='staff')

    def __str__(self):
        return str(self.start.strftime("%H:%M")) + '-' + str(self.end.strftime("%H:%M"))


class Immunization(models.Model):

    date = models.DateField()
    end = models.DateField(blank=True, null=True)
    type = models.CharField(max_length=64, choices=IMM_TYPE)
    amount = models.CharField(max_length=32)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    def __str__(self):
        return self.type

    class Meta:
        unique_together = ('type', 'patient', 'date'),


class Medication(models.Model):
    notes = models.CharField(max_length=256, blank=True, null=True)
    type = models.CharField(max_length=64)
    amount = models.CharField(max_length=16, blank=True, null=True)
    frequency = models.CharField(max_length=64)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    start = models.DateField(blank=True, null=True)
    finish = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.type


class PatientEm(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='em_pat')
    name = models.CharField(max_length=64)
    email = models.CharField(max_length=64, blank=True, null=True)
    phone1 = PhoneNumberField()
    phone2 = PhoneNumberField(blank=True, null=True)
    p_id = models.AutoField(primary_key=True)

    def __str__(self):
        return self.name


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
    deadline = models.DateTimeField()
    notes = models.CharField(max_length=256, blank=True, null=True)
    complete = models.BooleanField(default=False)
    name = models.CharField(max_length=20)
    set_by = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, null=True, related_name='setter')
    complete_by = models.ManyToManyField(
        Staff, default=DEFAULT_STAFF_EMAIL, related_name='doer')
    completion_date = models.DateTimeField(null=True, blank=True)
    actually_completed = models.ForeignKey(
        Staff, on_delete=models.SET_NULL, blank=True, null=True, related_name='completer')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('deadline', 'completion_date')


# instead of weight have like vitals measurements - weight, height, heart rate, blood pressure

class Weight(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()  # auto_now=True)
    value = models.IntegerField()

    def __str__(self):
        return str(self.value)

    class Meta:
        ordering = ('date',)


class Update(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=64, blank=True)
    body = models.TextField(max_length=256)
    date = models.DateTimeField(auto_now=True, blank=True)
    seen = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return self.title


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
