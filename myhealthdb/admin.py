from django.contrib import admin

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

# from myhealthdb.forms import CustomUserCreationForm, CustomUserChangeForm

from myhealthdb.models import Weight, CustomUser, Patient, PatientDoctor, Hospital, Ward, Staff, Activity, Condition, Document, Event, Immunization, Medication, PatientEm, Symptom, SymptomsSet, Task, Group

# Register your models here.

admin.site.register(Weight)
admin.site.register(Group)
admin.site.register(Patient)
admin.site.register(Hospital)
admin.site.register(Ward)
admin.site.register(Staff)
admin.site.register(PatientDoctor)
admin.site.register(Activity)
admin.site.register(Condition)
admin.site.register(Document)
admin.site.register(Event)
admin.site.register(Immunization)
admin.site.register(Medication)
admin.site.register(PatientEm)
admin.site.register(Symptom)
admin.site.register(SymptomsSet)
admin.site.register(Task)
