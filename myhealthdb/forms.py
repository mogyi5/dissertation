from django import forms
from myhealthdb.models import CustomUser, Patient, Staff, PatientEm, PatientDoctor, Event
from contact_form.forms import ContactForm
from captcha.fields import CaptchaField
from django.forms import inlineformset_factory
from datetimewidget.widgets import DateTimeWidget


PDSet = inlineformset_factory(Patient, PatientDoctor, fields = ['doctor', 'primary', 'note'],  can_delete=True, extra=1, max_num=5)
ECSet = inlineformset_factory(Patient, PatientEm, fields = ['name', 'email', 'phone1', 'phone2'],  can_delete=True, extra=1, max_num=5)

class PatientProfileForm(forms.ModelForm):
    
    class Meta:
        model = Patient
        exclude = ('baseuser','weight', 'height')

class StaffProfileForm(forms.ModelForm):
    
    class Meta:
        model = Staff
        exclude = ('baseuser',)

class EventBookingForm(forms.ModelForm):

    # title =  
    date_in = forms.DateTimeField()
    # date_out = forms.DateTimeInput()
    # relation 
    # type
    # notes

    class Meta:
        model = Event
        exclude = ('letter', 'date_out')


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
 
    REASON = (
        ('support', 'Support'),
        ('feedback', 'Feedback'),
        ('delete', 'Account deletion')
    )
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