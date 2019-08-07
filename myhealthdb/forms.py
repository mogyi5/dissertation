from django import forms
from myhealthdb.models import Task, CustomUser, Patient, Staff, PatientEm, PatientDoctor, Event, Medication, Condition, Document
from contact_form.forms import ContactForm
from captcha.fields import CaptchaField
from django.forms import inlineformset_factory
from datetimewidget.widgets import DateTimeWidget
from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput
from bootstrap_modal_forms.forms import BSModalForm
from django_select2.forms import Select2MultipleWidget
from myhealthdb.modelchoices import *

class DocumentForm(forms.ModelForm):
    class Meta:
            model = Document
            fields = ['name','file','description','type']


class ConditionForm(forms.ModelForm):

    class Meta:
        model = Condition
        fields = ['start','stop','type','reaction','severity','details','title']

class MedicationForm(forms.ModelForm):

    class Meta:
        model = Medication
        fields = ['type', 'notes', 'amount', 'frequency','start', 'finish']

class TaskForm(forms.ModelForm):
    # complete_by = ModelMultipleChoiceField(queryset=Staff.objects.all(), widget=Select2MultipleWidget)

    class Meta:
        model = Task
        fields = ['name', 'notes', 'complete_by', 'deadline']

        widgets = {
            'complete_by':Select2MultipleWidget,
        }


# class PatientSearchForm(SearchForm):
#     # first_name = forms.CharField(required=False)
#     # last_name = forms.CharField(required=False)
#     # dob = forms.DateTimeField(required=False)
#     # nhs_no = forms.CharField(required=False)
#     # ad_postcode = forms.CharField(required=False)

#     def search(self):
#         # First, store the SearchQuerySet received from other processing.
#         sqs = super(PatientSearchForm, self).search()

#         if not self.is_valid():
#             return self.no_query_found()

#         # Check to see if a start_date was chosen.
#         # if self.cleaned_data['first_name']:
#         #     sqs = sqs.filter(first_name=self.cleaned_data['first_name'])

#         # # Check to see if an end_date was chosen.
#         # if self.cleaned_data['end_date']:
#         #     sqs = sqs.filter(pub_date__lte=self.cleaned_data['end_date'])

#         return sqs


PDSet = inlineformset_factory(Patient, PatientDoctor, fields = ['doctor', 'primary', 'note'],  can_delete=True, extra=1, max_num=5)
ECSet = inlineformset_factory(Patient, PatientEm, fields = ['name', 'email', 'phone1', 'phone2'],  can_delete=True, extra=1, max_num=5)

class PatientProfileForm(forms.ModelForm):

    first_name = forms.CharField()
    last_name= forms.CharField()
    sex = forms.ChoiceField(choices = SEX)
    dob = forms.DateField()
    tel_no = forms.CharField(required = False)
    nhs_no = forms.CharField(required = False)
    ad_line1 = forms.CharField()
    ad_line2 = forms.CharField(required = False)
    ad_city = forms.CharField()
    ad_postcode = forms.CharField()
    ad_country = forms.CharField()    
    
    class Meta:
        model = Patient
        exclude = ('baseuser','weight', 'height')

class StaffProfileForm(forms.ModelForm):
    
    class Meta:
        model = Staff
        exclude = ('baseuser',)

class EventBookingForm(forms.ModelForm):

    # allrelationships = PatientDoctor.objects.filter()


    # title = forms.CharField()
    # date_in = forms.DateTimeField()
    # relation = forms.ModelChoiceField(queryset = PatientDoctor.objects.all()) #change this one
    # type = forms.ChoiceField(choices = EVENT_TYPE)
    # notes = forms.CharField()

    class Meta:
        model = Event
        fields = ('title', 'date_in', 'pd_relation', 'type', 'notes')
        # exclude = ('letter', 'date_out','done')

        # widgets = {
        #     'date_in': DateTimePickerInput(),
        #     'date_out': DateTimePickerInput(),
        # }


class PatientSignupForm(forms.Form):

    SEX  =(
        ('M', 'Male'),
        ('F', 'Female')
    )

    patient_first_name = forms.CharField(max_length=30, required=True, strip=True)
    patient_second_name =  forms.CharField(max_length=30, required=True, strip=True)
    patient_sex = forms.ChoiceField(choices = SEX)
    patient_dob = forms.DateField()
    patient_telno = forms.CharField(max_length=50, required=True, strip=True)
    ad_line1 = forms.CharField(max_length=64)
    ad_line2 = forms.CharField(max_length=64, required=False)
    ad_city = forms.CharField(max_length=32)
    ad_postcode = forms.CharField(max_length=32)
    ad_country = forms.CharField(max_length=32)    

    class Meta:
        widgets = {
            'patient_dob': DatePickerInput(),
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
            ad_line1 = self.cleaned_data.get('ad_line1'),
            ad_line2 = self.cleaned_data.get('ad_line2'),
            ad_city = self.cleaned_data.get('ad_city'),
            ad_postcode = self.cleaned_data.get('ad_postcode'),
            ad_country = self.cleaned_data.get('ad_country'),
        )

        patient_user.baseuser.save()
        patient_user.save()

        return patient_user.baseuser


class HospitalContactForm(ContactForm):
    def __init__(self, request, *args, **kwargs):
        super(HospitalContactForm, self).__init__(request=request, *args, **kwargs)
        fields_keyOrder = ['reason', 'name', 'email', 'body']
        if (self.fields.has_key('keyOrder')):
            self.fields.keyOrder = fields_keyOrder
        else:
            self.fields = OrderedDict((k, self.fields[k]) for k in fields_keyOrder)
 
    reason = forms.ChoiceField(choices=REASON, label='Reason')
    captcha = CaptchaField()
    template_name = 'contact_form/contact_form.txt'
    subject_template_name = "contact_form/contact_form_subject.txt"




    
# class StaffSignupForm(SignupForm):

#     TYPE  =(
#         ('2', 'Doctor'),
#         ('3', 'Receptionist')
#     )

#     staff_first_name = forms.CharField(max_length=30, required=True, strip=True)
#     staff_second_name = forms.CharField(max_length=30, required=True, strip=True)
#     staff_telno = forms.CharField(max_length=50, required=True, strip=True)
#     user_type_choice = forms.ChoiceField(choices = TYPE)

#     def save(self, request):

#         this_user = super(StaffSignupForm, self).save(request)
#         this_user.user_type = self.cleaned_data.get('user_type_choice')

#         staff_user = Staff(
#             baseuser = this_user,
#             first_name=self.cleaned_data.get('staff_first_name'),
#             second_name=self.cleaned_data.get('staff_second_name'),
#             tel_no = self.cleaned_data.get('staff_telno'),

#         )

#         staff_user.baseuser.save()
#         staff_user.save()

#         return staff_user.baseuser