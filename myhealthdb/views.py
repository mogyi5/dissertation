from django.shortcuts import render, redirect
from allauth.account.views import SignupView
from django.contrib.auth.decorators import login_required, user_passes_test
from myhealthdb.forms import PatientSignupForm, PatientProfileForm, StaffProfileForm, HospitalContactForm
from django.shortcuts import redirect
from myhealthdb.models import CustomUser, Patient, Staff
from django.views.generic.edit import FormView

def patient_check(user):
    if user.user_type == 1:
        return True
    return False

def staff_check(user):
    if user.user_type == 2 or user.user_type == 3:
        return True
    return False

def request_user_check(user):
    if id == request.user.id:
        return True
    return False

# Create your views here.
def index(request):

    context_dict = {}
    response = render(request, 'myhealthdb/index.html', context_dict)

    return response

def about(request):

    context_dict = {}
    response = render(request, 'myhealthdb/about_this.html', context_dict)

    return response

@user_passes_test(patient_check, redirect_field_name='home_base')
def patient_home(request, id):

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    patientprofile = Patient.objects.get_or_create(baseuser=baseuser)[0]

    # context_dict = {}
    response = render(request, 'myhealthdb/patient_home.html', {'patientprofile': patientprofile})

    return response

@user_passes_test(staff_check, redirect_field_name='home_base')
def staff_home(request,id):

    if id != request.user.id:
        return redirect('home_base')    

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    staffprofile = Staff.objects.get_or_create(baseuser=baseuser)[0]

    response = render(request, 'myhealthdb/staff_home.html', {'staffprofile': staffprofile})

    return response

#################################################################################################################################

@user_passes_test(patient_check, redirect_field_name='home_base')
def patient_details(request,id):

    if id != request.user.id:
        return redirect('home_base')    

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    patientprofile = Patient.objects.get_or_create(baseuser=baseuser)[0]
    form = PatientProfileForm({'dob':patientprofile.dob, 'first_name':patientprofile.first_name, 'last_name':patientprofile.last_name, 'sex':patientprofile.sex, 'tel_no':patientprofile.tel_no,'nhs_no':patientprofile.nhs_no, 'ad_line1':patientprofile.ad_line1, 'ad_line2':patientprofile.ad_line2, 'ad_city':patientprofile.ad_city, 'ad_postcode':patientprofile.ad_postcode, 'ad_country':patientprofile.ad_country} )


    if request.method == 'POST':
        form = PatientProfileForm(request.POST,instance=request.user.patient)

        if form.is_valid():
            # form.save()
            patientprofile = form.save(commit=False)
            patientprofile.save()
            return redirect('patient_home', id)
        else:
            form = PatientProfileForm(instance = request.user.patient)
            print(form.errors)


    context = {
        'form': form,
        'patientprofile' : patientprofile,
    }

    response = render(request, 'myhealthdb/patient_details.html', context)
    return response

@user_passes_test(staff_check, redirect_field_name='home_base')
def staff_details(request,id):

    if id != request.user.id:
        return redirect('home_base')    

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    staffprofile = Staff.objects.get_or_create(baseuser=baseuser)[0]
    form = StaffProfileForm({'tel_no':staffprofile.tel_no, 'first_name':staffprofile.first_name, 'last_name':staffprofile.last_name, 'ward':staffprofile.ward} )

    if request.method == 'POST':
        form = StaffProfileForm(request.POST,instance=request.user.staff)

        if form.is_valid():
            # form.save()
            staffprofile = form.save(commit=False)
            staffprofile.save()
            return redirect('staff_home', id)
        else:
            form = StaffProfileForm(instance = request.user.staff)
            print(form.errors)


    context = {
        'form': form,
        'staffprofile' : staffprofile,
    }

    response = render(request, 'myhealthdb/staff_details.html', context)
    return response


@login_required(redirect_field_name ='index')
def home_base(request):

    thisid = request.user.id
    if request.user.user_type == 1:
        return redirect('patient_home', id=thisid)
    else: 
        return redirect("staff_home", id=thisid)

# class StaffSignupView(SignupView):
#     template_name = 'account/signup_staff.html'
#     form_class = StaffSignupForm
#     view_name = 'staff_signup'

# staff_signup = StaffSignupView.as_view()


class HospitalContactFormView(FormView):
    form_class = HospitalContactForm
    template_name = 'contact_form/contact_form.html'
 
    def form_valid(self, form):
        human = True
        form.save()
        return super(HospitalContactFormView, self).form_valid(form)
 
    def get_form_kwargs(self):
        # ContactForm instances require instantiation with an
        # HttpRequest.
        kwargs = super(HospitalContactFormView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs
 
    def get_success_url(self):
        # This is in a method instead of the success_url attribute
        # because doing it as an attribute would involve a
        # module-level call to reverse(), creating a circular
        # dependency between the URLConf (which imports this module)
        # and this module (which would need to access the URLConf to
        # make the reverse() call).
        return reverse('contact_form_sent')
