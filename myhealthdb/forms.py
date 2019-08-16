from django import forms
from myhealthdb.models import CustomUser, Shift, Update, Ward, Task, CustomUser, Patient, Staff, PatientEm,Event, Medication, Condition, Document  #PatientDoctor, 
from contact_form.forms import ContactForm
from captcha.fields import CaptchaField
from django.forms import inlineformset_factory
from django.forms.models import modelformset_factory
from datetimewidget.widgets import DateTimeWidget
from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput, TimePickerInput
from bootstrap_modal_forms.forms import BSModalForm
from django_select2.forms import Select2MultipleWidget
from myhealthdb.modelchoices import *
from datetime import date
from mapwidgets.widgets import GooglePointFieldWidget
from phonenumber_field.formfields import PhoneNumberField
from django.core.exceptions import ValidationError

class ShiftForm(forms.ModelForm):

    class Meta:
        model=Shift
        fields = ['date', 'start', 'end', 'staff']

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")
        if end < start:
            raise forms.ValidationError("End should be later than start.")


##queryset only ppl in your ward
EventFormSet = modelformset_factory(Shift, form=ShiftForm, can_delete=True, extra=1,widgets={
    'date': DatePickerInput(), 'start': TimePickerInput(), 'end': TimePickerInput()})


class DocumentForm(forms.ModelForm):
    class Meta:
            model = Document
            fields = ['name','file','description','type']


class ConditionForm(forms.ModelForm):

    class Meta:
        model = Condition
        fields = ['start','stop','type','reaction','severity','details','title']

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("stop")
        if end < start:
            raise forms.ValidationError("Stop should be later than start.")

class MedicationForm(forms.ModelForm):

    class Meta:
        model = Medication
        fields = ['type', 'notes', 'amount', 'frequency','start', 'finish']

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("finish")
        if end < start:
            raise forms.ValidationError("Finish should be later than start.")


class TaskForm(forms.ModelForm):
    # complete_by = ModelMultipleChoiceField(queryset=Staff.objects.all(), widget=Select2MultipleWidget)

    class Meta:
        model = Task
        fields = ['name', 'notes', 'complete_by', 'deadline']

        widgets = {
            'complete_by':Select2MultipleWidget,
        }


# PDSet = inlineformset_factory(Patient, PatientDoctor, fields = ['doctor', 'primary', 'note'],  can_delete=True, extra=1, max_num=5)
ECSet = inlineformset_factory(Patient, PatientEm, fields = ['name', 'email', 'phone1', 'phone2'],  can_delete=True, extra=1, max_num=5)

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
        widgets = {
            'address': GooglePointFieldWidget,
        }

class StaffProfileForm(forms.ModelForm):
    
    class Meta:
        model = Staff
        exclude = ('baseuser',)

class EventBookingForm(forms.ModelForm):

    
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

    def signup(self, request, user):

        #this_user = super(PatientSignupForm, self).save(request)
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


class HospitalContactForm(forms.Form):

    # def __init__(self, request, *args, **kwargs):
    #     super(HospitalContactForm, self).__init__(request=request, *args, **kwargs)
    #     fields_keyOrder = ['reason', 'name', 'email', 'body']
    #     if (self.fields.has_key('keyOrder')):
    #         self.fields.keyOrder = fields_keyOrder
    #     else:
    #         self.fields = OrderedDict((k, self.fields[k]) for k in fields_keyOrder)
 
    reason = forms.ChoiceField(choices=REASON, label='Reason')
    captcha = CaptchaField()
    # template_name = 'contact_form/contact_form.txt'
    # subject_template_name = "contact_form/contact_form_subject.txt"


class CustomUserForm(forms.ModelForm):

    email = forms.EmailField()

    def save(self, commit=True):

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
    
class StaffSignupForm(forms.ModelForm):

    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)

    class Meta:
        model=Staff
        exclude = ['baseuser',]
