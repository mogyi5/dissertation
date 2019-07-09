from django.contrib import admin

from myhealthdb.models import Address, Patient, Hospital, Ward, Staff, PatientDoctor, Activity, Condition, Document, EmergencyContact, Event, Immunization, Medication, PatientEm, Symptom, SymptomsSet, Task

# Register your models here.

admin.site.register(Address)
admin.site.register(Patient)
admin.site.register(Hospital)
admin.site.register(Ward)
admin.site.register(Staff)
admin.site.register(PatientDoctor)
admin.site.register(Activity)
admin.site.register(Condition)
admin.site.register(Document)
admin.site.register(EmergencyContact)
admin.site.register(Event)
admin.site.register(Immunization)
admin.site.register(Medication)
admin.site.register(PatientEm)
admin.site.register(Symptom)
admin.site.register(SymptomsSet)
admin.site.register(Task)
