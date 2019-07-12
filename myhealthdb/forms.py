from django import forms
from myhealthdb.models import CustomUser, Address, Patient, Staff
from allauth.account.forms import SignupForm

class PatientProfileForm(forms.ModelForm):
    
    class Meta:
        model = Patient
        exclude = ('baseuser',)


class AddressForm(forms.ModelForm):

    class Meta:
        model = Address
        exclude = ()

class PatientSignupForm(SignupForm):

    SEX  =(
        ('M', 'Male'),
        ('F', 'Female')
    )

    patient_name = forms.CharField(max_length=50, required=True, strip=True)
    patient_sex = forms.ChoiceField(choices = SEX)
    patient_dob = forms.DateField()
    patient_telno = forms.CharField(max_length=50, required=True, strip=True)

    def save(self, request):

        this_user = super(PatientSignupForm, self).save(request)
        this_user.user_type =1


        patient_user = Patient(
            baseuser = this_user,
            name=self.cleaned_data.get('patient_name'),
            sex = self.cleaned_data.get('patient_sex'),
            dob = self.cleaned_data.get('patient_dob'),
            tel_no = self.cleaned_data.get('patient_telno'),
        )

        patient_user.baseuser.save()
        patient_user.save()

        return patient_user.baseuser

    
class StaffSignupForm(SignupForm):

    TYPE  =(
        ('2', 'Doctor'),
        ('3', 'Receptionist')
    )

    staff_name = forms.CharField(max_length=50, required=True, strip=True)
    staff_telno = forms.CharField(max_length=50, required=True, strip=True)
    user_type_choice = forms.ChoiceField(choices = TYPE)

    def save(self, request):

        this_user = super(StaffSignupForm, self).save(request)
        this_user.user_type = self.cleaned_data.get('user_type_choice')

        staff_user = Staff(
            baseuser = this_user,
            name=self.cleaned_data.get('staff_name'),
            tel_no = self.cleaned_data.get('staff_telno'),

        )

        staff_user.baseuser.save()
        staff_user.save()

        return staff_user.baseuser