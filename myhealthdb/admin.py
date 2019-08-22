from django.contrib import admin

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from django import forms
from easy_maps.widgets import AddressWithMapWidget
from mapwidgets.widgets import GooglePointFieldWidget

from myhealthdb.models import Shift, CustomUser, PatientHospital, Vital, CustomUser, Patient, Hospital, Ward, Staff, Condition, Document, Event, Immunization, Medication, PatientEm, Task, Group

#add address widget to hospital and patient
class HospitalAdmin(admin.ModelAdmin):

    class form(forms.ModelForm):
        class Meta:
            widgets = {
                'address':  GooglePointFieldWidget()
            }

class PatientAdmin(admin.ModelAdmin):

    class form(forms.ModelForm):
        class Meta:
            widgets = {
                'address':  GooglePointFieldWidget()
            }

#register all models in the admin
admin.site.register(Shift)
admin.site.register(CustomUser)
admin.site.register(PatientHospital)
admin.site.register(Vital)
admin.site.register(Group)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Hospital, HospitalAdmin)
admin.site.register(Ward)
admin.site.register(Staff)
admin.site.register(Condition)
admin.site.register(Document)
admin.site.register(Event)
admin.site.register(Immunization)
admin.site.register(Medication)
admin.site.register(PatientEm)
admin.site.register(Task)
