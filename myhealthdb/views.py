from django.shortcuts import render, redirect
from allauth.account.views import SignupView
from django.contrib.auth.decorators import login_required, user_passes_test
from myhealthdb.forms import PatientSignupForm, StaffSignupForm, AddressForm, PatientProfileForm
from django.shortcuts import redirect
from myhealthdb.models import CustomUser, Patient, Staff

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
    #context_dict = {}

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

    if request.method == 'POST':
        form_1 = AddressForm(request.POST)
        form_2 = PatientProfileForm(request.POST, initial={'name': patientprofile.name, 'dob':patientprofile.dob })

        if form_1.is_valid() and form_2.is_valid():
            form_1.save()
            form_2.save()
            return redirect('patient_home', id)
        else:
            print(form.errors)

    else:
        form_1 = AddressForm()
        form_2 = PatientProfileForm()

    

    context = {
        'form1': form_1,
        'form2': form_2,
        'patientprofile' : patientprofile,
    }

    return render(request, 'myhealthdb/patient_details.html', context)

    # patientprofile = Patient.objects.get_or_create(baseuser=baseuser)[0]
    # form = UserProfileForm({'about': userprofile.about, 'picture': userprofile.picture})

    # context_dict = {}
    # response = render(request, 'myhealthdb/patient_details.html', {'patientprofile': patientprofile})

    # return response

@user_passes_test(staff_check, redirect_field_name='home_base')
def staff_details(request,id):

    if id != request.user.id:
        return redirect('home_base')    

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    staffprofile = Staff.objects.get_or_create(baseuser=baseuser)[0]
    #context_dict = {}

    response = render(request, 'myhealthdb/staff_home.html', {'staffprofile': staffprofile})

    return response


class PatientSignupView(SignupView):

    template_name = 'account/signup_patient.html'
    form_class = PatientSignupForm
    view_name = 'patient_signup'

    def get_context_data(self, **kwargs):
        ret = super(PatientSignupView, self).get_context_data(**kwargs)
        ret.update(self.kwargs)
        return ret
    
patient_signup = PatientSignupView.as_view()


class StaffSignupView(SignupView):
    template_name = 'account/signup_staff.html'
    form_class = StaffSignupForm
    view_name = 'staff_signup'

staff_signup = StaffSignupView.as_view()


def home_base(request):

    if request.user.is_authenticated:
        thisid = request.user.id
        if request.user.user_type == 1:
            return redirect('patient_home', id=thisid)
        else: 
            return redirect("staff_home", id=thisid)
    else:
        return redirect("index")