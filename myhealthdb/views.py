from django.shortcuts import render, redirect
from allauth.account.views import SignupView
from django.contrib.auth.decorators import login_required, user_passes_test
from myhealthdb.forms import PatientSignupForm, PatientProfileForm, StaffProfileForm, HospitalContactForm, ECSet, PDSet, EventBookingForm
from django.shortcuts import redirect
from myhealthdb.models import CustomUser, Patient, Staff, PatientEm, Event, PatientDoctor
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db import transaction, IntegrityError
from django.contrib import messages
from time import sleep

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
def event_create(request, id):

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')
    
    if baseuser.user_type == 1:
        profile = Patient.objects.get_or_create(baseuser=baseuser)[0]
    else:
        profile = Staff.objects.get_or_create(baseuser=baseuser)[0]

    form = EventBookingForm()

    if request.method == 'POST':
        form = EventBookingForm(request.POST)

        if form.is_valid():
            # form.save()
            newevent = form.save(commit=False)
            newevent.save()
            return redirect('home_base', id)
        else:
            form = EventBookingForm()
            print(form.errors)


    context = {
        'form': form,
        'profile' : profile,
    }

    response = render(request, 'myhealthdb/event_create_form.html', context)

    return response


@user_passes_test(patient_check, redirect_field_name='home_base')
def patient_home(request, id):

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Patient.objects.get_or_create(baseuser=baseuser)[0]
    pdrelations = PatientDoctor.objects.get(patient = profile)
    events = pdrelations.reversepd.all()

    context = {
        'events': events,
        'profile' : profile,
    }
    response = render(request, 'myhealthdb/patient_home.html', context)

    return response

@user_passes_test(staff_check, redirect_field_name='home_base')
def staff_home(request,id):

    if id != request.user.id:
        return redirect('home_base')    

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile  = Staff.objects.get_or_create(baseuser=baseuser)[0]

    pdrelations = PatientDoctor.objects.get(doctor = profile)
    events = pdrelations.reversepd.all()

    context = {
        'events': events,
        'profile': profile,
    }
    
    response = render(request, 'myhealthdb/patient_home.html', context)

    return response

#################################################################################################################################

@user_passes_test(patient_check, redirect_field_name='home_base')
def patient_details(request, id):

    if id != request.user.id:
        return redirect('home_base')    

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Patient.objects.get_or_create(baseuser=baseuser)[0]
    form = PatientProfileForm({'dob':profile.dob, 'first_name':profile.first_name, 'last_name':profile.last_name, 'sex':profile.sex, 'tel_no':profile.tel_no,'nhs_no':profile.nhs_no, 'ad_line1':profile.ad_line1, 'ad_line2':profile.ad_line2, 'ad_city':profile.ad_city, 'ad_postcode':profile.ad_postcode, 'ad_country':profile.ad_country} )

    ecformset = ECSet(instance=request.user.patient)
    pdformset = PDSet(instance=request.user.patient)

    if request.method == 'POST':
        form = PatientProfileForm(request.POST,instance=request.user.patient)
        ecformset = ECSet(request.POST or None, request.FILES or None, instance = request.user.patient)
        pdformset = PDSet(request.POST or None, request.FILES or None, instance = request.user.patient)

        if form.is_valid() and ecformset.is_valid() and pdformset.is_valid():
            # form.save()
            profile = form.save(commit=False)
            profile.save()

            ecformset.save()
            pdformset.save()

            return redirect('patient_home', id)

        else:
            form = PatientProfileForm(instance = request.user.patient)
            ecformset = ECSet(request.GET or None, instance = request.user.patient)
            pdformset = PDSet(request.GET or None, instance = request.user.patient)
            print(form.errors)


    context = {
        'form': form,
        'ecformset': ecformset,
        'pdformset': pdformset,
        'profile' : profile,
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

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]
    form = StaffProfileForm({'tel_no':profile.tel_no, 'first_name':profile.first_name, 'last_name':profile.last_name, 'ward':profile.ward} )

    if request.method == 'POST':
        form = StaffProfileForm(request.POST,instance=request.user.staff)

        if form.is_valid():
            # form.save()
            profile = form.save(commit=False)
            profile.save()
            return redirect('staff_home', id)
        else:
            form = StaffProfileForm(instance = request.user.staff)
            print(form.errors)


    context = {
        'form': form,
        'profile' : profile,
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
        kwargs = super(HospitalContactFormView, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs
 
    def get_success_url(self):
        return reverse('contact_form_sent')
