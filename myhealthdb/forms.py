from django import forms
from myhealthdb.models import Vital, CustomUser, Shift, Ward, Task, CustomUser, Patient, Staff, PatientEm,Event, Medication, Condition, Document, PatientHospital, Immunization  #PatientDoctor, 
from contact_form.forms import ContactForm
from django.forms import inlineformset_factory
from django.forms.models import modelformset_factory
from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput, TimePickerInput
from django_select2.forms import Select2MultipleWidget
from myhealthdb.modelchoices import *
from datetime import date
from mapwidgets.widgets import GooglePointFieldWidget
from phonenumber_field.formfields import PhoneNumberField
from django.core.exceptions import ValidationError


#form for entering weight
class WeightForm(forms.ModelForm):

    #a custom field
    value = forms.DecimalField(label = 'Weight', help_text='weight in kg')

    #meta values, the model created is 'Vital', and there is only one field: 'value'
    class Meta:
        model = Vital
        fields = ['value']

#form for entering height
class HeightForm(forms.ModelForm):

    value = forms.DecimalField(label = 'Height', help_text='height in cm')

    class Meta:
        model = Vital
        fields = ['value']

#form for staff to input immunizations
class ImmunizationForm(forms.ModelForm):

    #get the patient from the context in the views, call it user, set the patient choicefield to only include the patient passed through
    def __init__(self, user, *args,**kwargs):
        self.user = user
        self.pat = Patient.objects.filter(baseuser=self.user.baseuser)
        super(ImmunizationForm,self ).__init__(*args,**kwargs) 
        self.fields['patient'].queryset = self.pat

    class Meta:
        model = Immunization
        fields = ['date', 'end', 'type', 'amount', 'patient']


#form for entering shifts when doctors are working
class ShiftForm(forms.ModelForm):

    class Meta:
        model=Shift
        fields = ['date', 'start', 'end', 'staff']

    #clean the data to ensure the start date is not after the end date
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")
        if end and start:
            if end < start:
                raise forms.ValidationError("End should be later than start.")

#formset for creating shifts as the IT admin, for all the staff
EventFormSet = modelformset_factory(Shift, form=ShiftForm, can_delete=True, extra=1,widgets={
    'date': DatePickerInput(), 'start': TimePickerInput(), 'end': TimePickerInput()})

#form for doctor to add a document to a patient
class DocDocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ['name','pdf_file','description','type', 'patient']

    #pass patient to initial form, set choicefield to patient
    def __init__(self, user, *args,**kwargs):
        self.user = user
        self.ph = Patient.objects.filter(baseuser=self.user.baseuser)
        super(DocDocumentForm,self ).__init__(*args,**kwargs) 
        self.fields['patient'].queryset = self.ph

#form for patient to upload a document
class DocumentForm(forms.ModelForm):
    class Meta:
            model = Document
            fields = ['name','pdf_file','description','type']

#form for doctor to enter a condition
class DoctorConditionForm(forms.ModelForm):

    class Meta:
        model = Condition
        fields = ['start','stop','type','reaction','severity','details','title', 'patient']


    #clean the data to ensure the start date is not after the end date
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("stop")
        if end and start:
            if end < start:
                raise forms.ValidationError("Stop should be later than start.")

    #pass patient to initial form, set choicefield to patient
    def __init__(self, user, *args,**kwargs):
        self.user = user
        self.ph = Patient.objects.filter(baseuser=self.user.baseuser)
        super(DoctorConditionForm,self ).__init__(*args,**kwargs) 
        self.fields['patient'].queryset = self.ph

#form for patient to enter condition
class ConditionForm(forms.ModelForm):

    class Meta:
        model = Condition
        fields = ['start','stop','type','reaction','severity','details','title']

    #clean the data to ensure the start date is not after the end date
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("stop")
        if end and start:
            if end < start:
                raise forms.ValidationError("Stop should be later than start.")

#form for staff to add medication to patient's data
class DoctorMedicationForm(forms.ModelForm):

    class Meta:
        model = Medication
        fields = ['type', 'notes', 'amount', 'frequency','start', 'finish', 'patient']

    def __init__(self, user, *args,**kwargs):
        self.user = user
        self.ph = Patient.objects.filter(baseuser=self.user.baseuser)
        super(DoctorMedicationForm,self ).__init__(*args,**kwargs) 
        self.fields['patient'].queryset = self.ph

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("finish")
        if end and start:
            if end < start:
                raise forms.ValidationError("Finish should be later than start.")

#form for patient to input medication taken
class MedicationForm(forms.ModelForm):

    class Meta:
        model = Medication
        fields = ['type', 'notes', 'amount', 'frequency','start', 'finish']

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("finish")
        if end and start:
            if end < start:
                raise forms.ValidationError("Finish should be later than start.")

#form for creating a task for staff
class TaskForm(forms.ModelForm):
    
    class Meta:
        model = Task
        fields = ['name', 'notes', 'complete_by', 'deadline']

        #add a multiple select widget to the 'complete_by' field
        widgets = {
            'complete_by':Select2MultipleWidget,
        }


#formset for creating emergency contacts for the patient. it allows multiple object creation
ECSet = inlineformset_factory(Patient, PatientEm, fields = ['name', 'email', 'phone1', 'phone2'],  can_delete=True, extra=2, max_num=2)

#form for patient to update their information
class PatientProfileForm(forms.ModelForm):

    first_name = forms.CharField()
    last_name= forms.CharField()
    sex = forms.ChoiceField(choices = SEX)
    dob = forms.DateField(widget=DatePickerInput)
    tel_no = PhoneNumberField(required = False)
    nhs_no = forms.CharField(required = False)
    flat_no = forms.CharField(required = False)
    address = forms.CharField(widget=GooglePointFieldWidget())    
    
    class Meta:
        model = Patient
        exclude = ('baseuser','weight', 'height')
        #using the address widget
        widgets = {
            'address': GooglePointFieldWidget,
        }

#form for staff to update their information
class StaffProfileForm(forms.ModelForm):
    
    class Meta:
        model = Staff
        #include all other fields from the model but these
        exclude = ('baseuser', 'ward')

#form for event booking for staff, such as appointments
class StaffEventBookingForm(forms.ModelForm):
    
    #custom field
    pd_relation = forms.ModelChoiceField(label='Patient', required=True, queryset=None)

    #set the queryset for the patienthospital to show only patients from the staff's hospital
    def __init__(self, hospital, *args,**kwargs):
        self.hospital = hospital
        self.ph = PatientHospital.objects.filter(hospital=self.hospital, status=True)
        super(StaffEventBookingForm,self ).__init__(*args,**kwargs) 
        self.fields['pd_relation'].queryset = self.ph

    class Meta:
        model = Event
        fields = ('title', 'date_in', 'pd_relation', 'notes', 'type')

#form for event booking for staff, such as appointments
class EventBookingForm(forms.ModelForm):

    pd_relation = forms.ModelChoiceField(label='Practice', required=True, queryset=None)

    #set the queryset for the patienthospital to show only hospitals which the patient is registered with
    def __init__(self, user, *args,**kwargs):
        self.user = user
        self.ph = PatientHospital.objects.filter(patient=self.user, status=True)
        super(EventBookingForm,self ).__init__(*args,**kwargs) 
        self.fields['pd_relation'].queryset = self.ph

    #when saving, set the type to consultation - patients can only book appointments not surgeries
    def save(self, commit=True):
        event = Event(
            title=self.cleaned_data.get('title'),
            date_in=self.cleaned_data.get('date_in'),
            pd_relation = self.cleaned_data.get('pd_relation'),
            notes = self.cleaned_data.get('notes'),
            type = "Consultation"
        )
        event.save()

        return event

    class Meta:
        model = Event
        fields = ('title', 'date_in', 'pd_relation', 'notes')

#form for patients to sign up, including all of their details
class PatientSignupForm(forms.Form):

    patient_first_name = forms.CharField(label='First Name', max_length=30, required=True, strip=True)
    patient_second_name =  forms.CharField(label='Last Name', max_length=30, required=True, strip=True)
    patient_sex = forms.ChoiceField(label='Sex', choices = SEX)
    patient_dob = forms.DateField(label='Date of Birth', widget=DatePickerInput())
    patient_telno = PhoneNumberField(label='Telephone Number', required=True, strip=True)
    address = forms.CharField(label='Address', max_length=256, widget=GooglePointFieldWidget() )

    class Meta:
        model=Patient
        fields = ['first_name', 'last_name', 'dob','sex', 'telno', 'address']
        widgets = {
            'patient_dob': DatePickerInput(),
            'address': GooglePointFieldWidget()
        }

    #create a customuser (parent user) to the patient, as well as the patient object
    def signup(self, request, user):
        user.user_type =1

        patient_user = Patient(
            baseuser = user,
            first_name=self.cleaned_data.get('patient_first_name'),
            last_name=self.cleaned_data.get('patient_second_name'),
            sex = self.cleaned_data.get('patient_sex'),
            dob = self.cleaned_data.get('patient_dob'),
            tel_no = self.cleaned_data.get('patient_telno'),
            address = self.cleaned_data.get('address'),
        )

        patient_user.baseuser.user_type=1
        patient_user.baseuser.save()
        patient_user.save()

        return patient_user.baseuser

#form for hospitals to conatct 
class HospitalContactForm(forms.Form):

    def __init__(self, request, *args, **kwargs):
        super(HospitalContactForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(HospitalContactForm, self).save(commit=True)
        return instance
 
    reason = forms.ChoiceField(choices=REASON, label='Reason')

#form for creating just the customuser
class CustomUserForm(forms.ModelForm):

    email = forms.EmailField()

    def save(self, commit=True):

        #set the date joined to be today
        today = date.today()
        base = CustomUser(
            password=self.cleaned_data.get('password'),
            email=self.cleaned_data.get('email'),
            user_type = self.cleaned_data.get('user_type'),
            username = self.cleaned_data.get('email'),
            date_joined = today
        )
        base.save()

        return base

    class Meta:
        model=CustomUser
        fields = ['password', 'email', 'user_type']
    
#form for staff to be signed up by the it_guy
class StaffSignupForm(forms.ModelForm):

    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)

    class Meta:
        model=Staff
        exclude = ['baseuser',]
