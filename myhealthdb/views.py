from django.shortcuts import render, redirect, get_object_or_404
from allauth.account.views import SignupView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from myhealthdb.forms import HeightForm, WeightForm, StaffEventBookingForm, EventFormSet, CustomUserForm, StaffSignupForm, DocDocumentForm, DoctorMedicationForm, TaskForm, DoctorConditionForm, ImmunizationForm, PatientSignupForm, PatientProfileForm, StaffProfileForm, HospitalContactForm, ECSet,  EventBookingForm, MedicationForm, ConditionForm, DocumentForm  # PDSet,
from myhealthdb.models import Vital, Shift, Task, Ward, CustomUser, Patient, Staff, PatientEm, Event, Group, Medication, Condition, Immunization, Document, PatientHospital, Hospital  # PatientDoctor,
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic import DetailView, TemplateView
from django.urls import reverse_lazy
from django.db import transaction, IntegrityError
from django.db.models import Count, Sum
from django.contrib import messages
from time import sleep
from django.utils import timezone
from datetime import date, datetime, timedelta
from django.contrib.postgres.search import SearchVector
from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput, TimePickerInput
from django_select2.forms import Select2MultipleWidget
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, Http404, JsonResponse
try:
    from django.utils import simplejson as json
except ImportError:
    import json
from myhealthdb_project.settings import MEDIA_ROOT, MEDIA_URL
from django.template.loader import render_to_string, get_template
from mapwidgets.widgets import GooglePointFieldWidget
from django.contrib.gis import gdal
from geopy.geocoders import Nominatim, GoogleV3
from geopy import distance
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from django.db.models import Q


# the key for the google api, to use maps
geolocator = GoogleV3(api_key="AIzaSyCzCYVvHq7yit0ESbH-OLn8r0dA4WiMb8I")

# ----------------------------view checks, to ensure right person view the right view------------------------

# check privileges based on the customuser user_type, which determines whether a user is staff or patient


def patient_check(user):
    if user.user_type == 1:
        return True
    return False


def staff_check(user):
    if user.user_type == 2 or user.user_type == 3 or user.user_type == 4:
        return True
    return False


def it_check(user):
    if user.user_type == 4:
        return True
    return False


def request_user_check(user):
    if id == request.user.id:
        return True
    return False

# --------------------------------------actual views------------------------------------------------------
# most of these views have some similarities, such as getting the baseuser id and firguring out which user to pass to context.
# therefore i will only comment on things that you may see for the first time, but not all of it (it's 2000 lines of code.)
# hope it makes sense, the logic is not that difficult with these views!


def help(request, id):

    context = {}

    # if you are trying to look at someone else's help page, redirect to home_base
    if id != request.user.id:
        return redirect('home_base')

    # if id does not exist, go back to index
    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    # get the patient or staff profile
    try:
        profile = Patient.objects.get(baseuser=baseuser)
    except Patient.DoesNotExist:
        profile = Staff.objects.get(baseuser=baseuser)

    # add profile to context
    context['profile'] = profile

    # return a response, including the context.
    response = render(request, 'myhealthdb/help.html', context)

    return response


@user_passes_test(patient_check, redirect_field_name='home_base')
def WeightCreateView(request, id):

    context = {}
    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Patient.objects.get_or_create(baseuser=baseuser)[0]

    # set the form to be weight form
    form = WeightForm()

    if request.method == 'POST':

        # yesterday = today-1day
        yesterday = timezone.now() - timedelta(days=1)

        # if there was already a weight submitted today, redirect witout doing anything, can only post once per day.
        if Vital.objects.filter(patient=profile, type='Weight', date__gt=yesterday).exists():
            return redirect('home_base')

        # set form to requets post
        form = WeightForm(request.POST or None,
                          request.FILES or None)

        # if form is valid, set the patient to be the currently logged in patient, the type to weight, then save it and redirect
        if form.is_valid():
            weight = form.save(commit=False)
            weight.patient = profile
            weight.type = 'Weight'
            weight.save()
            return redirect('vitals', id=id)
        else:
            # if form is not valid, print errors
            # form = WeightForm(request.GET or None)
            print(form.errors)

    # add data to context
    context['form'] = form
    context['profile'] = profile

    response = render(
        request, 'vitals/weight_create_view.html', context)

    return response


# same as the weight view, just for the height - can post more than once a day though
@user_passes_test(patient_check, redirect_field_name='home_base')
def HeightCreateView(request, id):

    context = {}
    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Patient.objects.get_or_create(baseuser=baseuser)[0]

    form = HeightForm()

    if request.method == 'POST':
        form = HeightForm(request.POST or None,
                          request.FILES or None)

        if form.is_valid():
            height = form.save(commit=False)
            height.patient = profile
            height.type = 'Height'
            height.save()
            return redirect('vitals', id=id)
        else:
            # form = HeightForm(request.GET or None)
            print(form.errors)

    context['form'] = form
    context['profile'] = profile

    response = render(
        request, 'vitals/height_create_view.html', context)

    return response

# this view passes the weight data for the graph in vitals.
# part of the django restful api


class WeightData(APIView):

    # do not need any classes for this, it's only a graph
    authentication_classes = []
    permission_classes = []

    def put(self, request, *args, **kwargs):
        id = kwargs.get('id', 'Default')

    # get all the information here

    def get(self, request, *args, **kwargs):
        id = kwargs.get('id', 'Default')

        # get the logged in profile info
        baseuser = CustomUser.objects.get(id=id)
        profile = Patient.objects.get(baseuser=baseuser)

        start_date = {}
        end_date = {}
        try:
            # get the earliest and latest date for the weights of the patient
            start_date_list = Vital.objects.filter(
                patient=profile, type='Weight').order_by('date')
            end_date_list = Vital.objects.filter(
                patient=profile, type='Weight').order_by('-date')

            if start_date_list and end_date_list:
                start_date = start_date_list[0].date
                end_date = end_date_list[0].date

        except Vital.DoesNotExist:
            pass

        

        # calculate the time period between the start and end dates, and add the days inbetween to the graph labels
        labels = []
        difference = end_date-start_date
        for i in range(difference.days + 1):
            labels.append(start_date + timedelta(days=i))

        # the result is an array, the same length as the labels. if there was a weight recorded on that label day, add the value, else add 'None', so the graph remains continuous
        result = []
        weight = Vital.objects.filter(patient=profile, type="Weight")

        for i in range(len(labels)):
            for j in range(len(weight)):
                if labels[i] == weight[j].date:
                    result.append(weight[j].value)
                    break
                elif j == len(weight)-1:
                    result.append(None)

        data = {
            "labels": labels,
            "default": result,
        }
        return Response(data)

# a class based view, supposed to make life much easier. it does not.
# it is a deleteview which deletes an object, and the userpassestestmixin means that the user must pass a test (staff_check) to proceed to this page


class PatientHospitalDeleteView(UserPassesTestMixin, DeleteView):

    # deleting from patienthospital
    model = PatientHospital
    template_name = 'doctors_reg/doctors_delete.html'

    # when done, redirect here
    success_url = reverse_lazy('home_base')

    # the test the user must pass
    def test_func(self):
        return staff_check(self.request.user)

    # get the context data for the staff, their profile, groups and tasks in the sidebar.
    def get_context_data(self, **kwargs):
        context = super(PatientHospitalDeleteView,
                        self).get_context_data(**kwargs)
        context['event'] = self.object
        if self.request.user.user_type == 1:
            profile = Patient.objects.get_or_create(
                baseuser=self.request.user)[0]
        else:
            profile = Staff.objects.get_or_create(
                baseuser=self.request.user)[0]
        try:
            groups = Group.objects.filter(members=profile)
            context['groups'] = groups
        except Group.DoesNotExist:
            pass

        try:
            tasks = Task.objects.filter(complete_by=profile, complete=False)
            context['tasks'] = tasks
        except Task.DoesNotExist:
            pass

        context['profile'] = profile
        return context


@user_passes_test(staff_check, redirect_field_name='home_base')
def ImmunizationCreateView(request, id, pk):

    context = {}
    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]

    # pass the staff's groups and tasks to the template to be shown in the sidebar.
    try:
        groups = Group.objects.filter(members=profile)
        context['groups'] = groups
    except Group.DoesNotExist:
        pass

    try:
        tasks = Task.objects.filter(complete_by=profile, complete=False)
        context['tasks'] = tasks
    except Task.DoesNotExist:
        pass

    # get the patient object from the pk, same as staff but a different number so we can refer to it when creating the immunization object
    patient = {}
    try:
        base = CustomUser.objects.get(id=pk)
        try:
            patient = Patient.objects.get(baseuser=base)
        except Patient.DoesNotExist:
            return redirect('home_base')

    except CustomUser.DoesNotExist:
        return redirect('home_base')

    # create the form, set the widgets for the dates to be datepickerinput, and set their minimum and maximum dates.
    form = ImmunizationForm(user=patient)
    form.fields['date'].widget = DatePickerInput(options={
        # the date the injection was given, makes sense to input past injections but not future ones.
        'maxDate': ((datetime.today() + timedelta(hours=1)).strftime('%Y-%m-%d')),
    })
    form.fields['end'].widget = DatePickerInput(options={
        # the best before date of the injection, probably will last for at least 4 weeks
        'minDate': ((datetime.today() + timedelta(weeks=4)).strftime('%Y-%m-%d')),
    })

    # standard post form methods
    if request.method == 'POST':
        form = ImmunizationForm(patient, request.POST)

        if form.is_valid():
            # form.save()
            newimmu = form.save(commit=False)
            newimmu.added_by = profile.baseuser
            newimmu.save()
            return redirect('patient_view', id=id, pk=pk)
        else:
            # form = ImmunizationForm(user=patient)
            print(form.errors)

    context['form'] = form
    context['profile'] = profile

    response = render(
        request, 'immunizations/immunizations_create_view.html', context)

    return response

# patient details view


@user_passes_test(staff_check, redirect_field_name='home_base')
def patient_view(request, id, pk):
    context = {}

    # get the staff
    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]
    context['profile'] = profile

    # get the staff's groups and tasks in the sidebar
    try:
        groups = Group.objects.filter(members=profile)
        context['groups'] = groups
    except Group.DoesNotExist:
        pass

    try:
        tasks = Task.objects.filter(complete_by=profile, complete=False)
        context['tasks'] = tasks
    except Task.DoesNotExist:
        pass

    patient = {}

    # try to get the patient object, if it doesn't exist, go to home base
    try:
        patient = Patient.objects.get(baseuser_id=pk)

        try:
            pathospitals = PatientHospital.objects.get(
                hospital=profile.ward.hospital, patient=patient, status=True)

            # pass all of the patients data to this template for the doctor to see.
            context['pathospitals'] = pathospitals
            context['patient'] = patient
            context['patientem'] = PatientEm.objects.filter(patient=patient)
            context['conditions'] = Condition.objects.filter(patient=patient)
            context['medications'] = Medication.objects.filter(patient=patient)
            height={}
            try:
                height = Vital.objects.get(patient=patient, type='Height')
            except Vital.DoesNotExist:
                pass

            context['height'] = height

            weight={}
            try:
                weight_list = Vital.objects.filter(
                    patient=patient, type="Weight")
                if weight_list:
                    weight = weight_list.order_by('-id')[0]
            except Vital.DoesNotExist:
                pass

            context['weight'] = weight
            context['immunizations'] = Immunization.objects.filter(
                patient=patient)
            context['documents'] = Document.objects.filter(patient=patient)
        except PatientHospital.DoesNotExist:
            return redirect('home_base')

    except Patient.DoesNotExist:
        return redirect('home_base')

    response = render(request, 'search/patient_details.html', context)

    return response

# seen similar before!


class ShiftDeleteView(UserPassesTestMixin, DeleteView):
    model = Shift
    template_name = "admin_things/shift_delete_view.html"
    success_url = reverse_lazy('home_base')

    def test_func(self):
        return it_check(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ShiftDeleteView, self).get_context_data(**kwargs)
        profile = Staff.objects.get_or_create(
            baseuser=self.request.user)[0]
        context['profile'] = profile
        return context

# seen similar before!


class ShiftUpdateView(UserPassesTestMixin, UpdateView):
    model = Shift
    fields = ('start', 'end', 'date', 'staff')
    template_name = 'admin_things/shift_update_form.html'
    success_url = reverse_lazy('home_base')

    def test_func(self):
        return it_check(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ShiftUpdateView, self).get_context_data(**kwargs)
        context['shift'] = self.object
        profile = Staff.objects.get_or_create(
            baseuser=self.request.user)[0]
        context['profile'] = profile
        return context

    # get the form data from the template and change the widgets to sexier ones.
    def get_form(self):
        form = super().get_form()
        form.fields['date'].widget = DatePickerInput()
        form.fields['start'].widget = TimePickerInput()
        form.fields['end'].widget = TimePickerInput()
        return form

# user must be it guy


@user_passes_test(it_check, redirect_field_name='home_base')
def add_schedule(request, id):

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]
    context = {
        'profile': profile,
    }

    # similar to previous forms, but here it is a formset instead - many forms in one,
    # so we have to loop over each form and save it individually
    efformset = EventFormSet(prefix="foo",)

    if request.method == 'POST':
        efformset = EventFormSet(request.POST or None,
                                 request.FILES or None, prefix="foo")

        if efformset.is_valid():

            for f in efformset:
                f.save()

            return HttpResponseRedirect(reverse_lazy('home_base'))

        else:
            print(form.errors)
            # efformset = EventFormSet(request.GET or None, prefix="foo")

    context['efformset'] = efformset

    response = render(request, 'admin_things/schedule_create.html', context)

    return response

# seen similar before!


class StaffDeleteView(UserPassesTestMixin, DeleteView):
    model = Staff
    template_name = "admin_things/staff_delete_view.html"
    success_url = reverse_lazy('home_base')

    def test_func(self):
        return it_check(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(StaffDeleteView, self).get_context_data(**kwargs)
        profile = Staff.objects.get_or_create(
            baseuser=self.request.user)[0]
        context['profile'] = profile
        return context

# user must be an it person


@user_passes_test(it_check, redirect_field_name='home_base')
def StaffCreateView(request, id):
    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]
    context = {
        'profile': profile,
    }

    # similar to before, but here there are two forms, both are created and used with post methods, then saved.
    form = StaffSignupForm()
    baseform = CustomUserForm()

    if request.method == 'POST':
        form = StaffSignupForm(request.POST or None,
                               request.FILES or None)
        baseform = CustomUserForm(request.POST or None,
                                  request.FILES or None)

        if form.is_valid() and baseform.is_valid():
            base = baseform.save()

            staff = form.save(commit=False)
            staff.baseuser = base
            staff.save()

            return redirect('hospital_details', id=id)

        else:
            print(form.errors)
            # form = StaffSignupForm(request.GET or None)
            # baseform = CustomUserForm(request.GET or None)

    baseform.auto_id = True

    context['form'] = form
    context['baseform'] = baseform

    response = render(request, 'admin_things/staff_create_form.html', context)

    return response


@user_passes_test(it_check, redirect_field_name='home_base')
def hospital_details(request, id):
    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]
    context = {
        'profile': profile,
    }

    hospital = Hospital.objects.get(id=profile.ward.hospital.id)

    wards = Ward.objects.filter(hospital=hospital)

    # total number of wards in the hospital
    totalwards = wards.count()
    context['totalwards'] = totalwards

    # what staff are in what wards
    individualstaff = wards.annotate(
        staffnumber=Count('current_ward')).values()
    context['individualstaff'] = individualstaff

    # how many staff altogether in the hospital?
    totalstaff = individualstaff.aggregate(Sum('staffnumber'))
    context['totalstaff'] = totalstaff

    staff = Staff.objects.filter(ward__in=wards)

    context['staff'] = staff

    # change the format of the address, it is stored like POINT(2.4454 4.5564) but we want 4.5564, 2.4454 for the geopy api to work
    prev_address = hospital.address
    prev_address = prev_address[7:-1]
    splits = prev_address.split(" ")
    prev_address = prev_address.replace(" ", ",")
    swap_address = prev_address.split(",")
    h_address = swap_address[1] + "," + swap_address[0]
    new_address = geolocator.reverse(h_address, exactly_one=True)
    context['new_address'] = new_address

    patientnumber = PatientHospital.objects.filter(
        hospital=hospital, status=True).count()
    context['patientnumber'] = patientnumber

    context['hospital'] = hospital

    response = render(request, 'admin_things/hospital_staff.html', context)

    return response

# a list view of all the patients in the hospital


class PatientView(UserPassesTestMixin, ListView):
    model = Patient
    template_name = "search/patient_view.html"

    def test_func(self):
        return staff_check(self.request.user)

    def get_queryset(self):
        # get the object of the user's current hospital
        hospital = Hospital.objects.get(
            name=self.request.user.doctor.ward.hospital.name)
        patienthospitals = PatientHospital.objects.filter(
            hospital=hospital, status=True).values('patient')
        if patienthospitals:
            # only get the patiets in this hospital
            new_context = Patient.objects.filter(
                baseuser_id__in=patienthospitals).order_by('last_name')
        else:
            new_context = {}
        return new_context

    def get_context_data(self, **kwargs):
        context = super(PatientView, self).get_context_data(**kwargs)
        profile = Staff.objects.get_or_create(
            baseuser=self.request.user)[0]
        try:
            groups = Group.objects.filter(members=profile)
            context['groups'] = groups
        except Group.DoesNotExist:
            pass

        try:
            tasks = Task.objects.filter(complete_by=profile, complete=False)
            context['tasks'] = tasks
        except Task.DoesNotExist:
            pass
        context['profile'] = profile
        return context

# json response for rejecting a patient, comes up with an alert


@user_passes_test(staff_check, redirect_field_name='home_base')
def reject_patient(request):

    if request.method == 'POST':

        id = request.POST.get('id', None)
        patienthospital = PatientHospital.objects.get_or_create(id=id)[0]

        # delete patienthospital completely, as the patient is rejected
        patienthospital.delete()
        message = 'The patient has been rejected'

    ctx = {'message': message}

    return HttpResponse(json.dumps(ctx), content_type='application/json')

# json response for accepting a patient, comes up with an alert


@user_passes_test(staff_check, redirect_field_name='home_base')
def accept_patient(request):

    if request.method == 'POST':

        id = request.POST.get('id', None)
        patienthospital = PatientHospital.objects.get_or_create(id=id)[0]

        # set patienthospital status to true = the user has been accepted
        patienthospital.status = True
        patienthospital.save()
        message = 'The patient has been registered'

    ctx = {'message': message}

    return HttpResponse(json.dumps(ctx), content_type='application/json')


# another json reponse, here the patient tries to register with the hospital
@user_passes_test(patient_check, redirect_field_name='home_base')
def register_hospital(request):

    if request.method == 'POST':
        user = request.user
        patient = Patient.objects.get_or_create(baseuser=user)[0]
        id = request.POST.get('id', None)
        hospital = Hospital.objects.get_or_create(id=id)[0]

        exists = False
        try:
            existing = PatientHospital.objects.get(
                patient=patient, hospital=hospital)
            exists = True
        except PatientHospital.DoesNotExist:
            pass

        if exists:
            # if there is a patienthospital object alreayd with the hospital, do nothing, just an alert
            message = 'You are already registered with this hospital.'
        else:
            # else create a new patienthospital object, with status=false by default
            ph = PatientHospital(patient=patient, hospital=hospital)
            ph.save()
            message = 'You have sent your details to the practice. They will get back to you shortly.'

    ctx = {'message': message}
    return HttpResponse(json.dumps(ctx), content_type='application/json')

# view for patient to see all their patienthospital objects


@user_passes_test(patient_check, redirect_field_name='home_base')
def doctors_view(request, id):
    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Patient.objects.get_or_create(baseuser=baseuser)[0]
    context = {
        'profile': profile,
    }

    # separate pending and confirmed registrations
    try:
        pending_hosp = PatientHospital.objects.filter(
            patient=profile, status=False).values('hospital')
        r_pending = Hospital.objects.filter(id__in=pending_hosp)
        context['r_pending'] = r_pending

        # get the wards in each of the hospitals for display
        wards = Ward.objects.filter(hospital__in=pending_hosp)
        context['w_pending'] = wards
    except PatientHospital.DoesNotExist:
        pass

    try:
        confirmed_hosp = PatientHospital.objects.filter(
            patient=profile, status=True).values('hospital')
        r_confirmed = Hospital.objects.filter(id__in=confirmed_hosp)
        context['r_confirmed'] = r_confirmed

        # get the wards in each of the hospitals for display
        c_wards = Ward.objects.filter(hospital__in=confirmed_hosp)
        context['w_confirmed'] = c_wards
    except PatientHospital.DoesNotExist:
        pass

    response = render(request, 'doctors_reg/doctors_view.html', context)

    return response

# the view which shows the nearest hospitals, passes the hospital objects to it and shows distance.


@user_passes_test(patient_check, redirect_field_name='home_base')
def doctors_reg(request, id):

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Patient.objects.get_or_create(baseuser=baseuser)[0]
    context = {
        'profile': profile,
    }

    # change the address, like before, to be fit for use in geopy.
    profileaddress = profile.address
    profilecutaddress = profileaddress[7:-1]
    profilecutaddress = profilecutaddress.replace(" ", ",")
    location = geolocator.reverse(profilecutaddress)

    # list of all hospitals
    openhospitals = Hospital.objects.filter(taking_patients=True)

    closest = []
    largest = 0
    largestmember = ''

    # shows the 10 closest hospitals
    maxim = 10

    # a method which takes each hospital in turn,
    for i in range(0, len(openhospitals)):

        # fixes their address to be good to use,
        data_array = {}
        address = openhospitals[i].address
        cutaddress = address[7:-1]
        cutaddress = cutaddress.replace(" ", ",")

        # calculate the distance to the patient's address,
        thedistance = distance.distance(
            profilecutaddress, cutaddress).miles  # change from km to miles

        # add all data to an array,
        c_wards = Ward.objects.filter(hospital=openhospitals[i])
        data_array[0] = openhospitals[i]
        data_array[1] = thedistance
        data_array[2] = c_wards

        # then loop through the existing hospitals in the 'closest' array and slot it in to the right place,  i.e. smaller distance than the next one but greater than the previous one.
        if closest:
            for k in range(0, len(closest)):
                if len(closest) < maxim:
                    if thedistance <= closest[k][1] or len(closest) < maxim:
                        closest.insert(k+1, data_array)
                        break
                else:
                    if thedistance <= closest[k][1]:
                        closest.insert(k+1, data_array)
                        del closest[k]
                        break
        else:
            closest.append(data_array)
    context['closest'] = closest

    response = render(request, 'doctors_reg/doctors_reg.html', context)

    return response

# show groups, send data in json format


def autocompleteGroup(request, id):

    ctx = {}
    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]
    ctx['profile'] = profile

    url_parameter = request.GET.get("q")

    if url_parameter:
        groups = Group.objects.filter(name__icontains=url_parameter)
    else:
        groups = Group.objects.all()

    ctx["groups"] = groups

    if request.is_ajax():
        html = render_to_string(
            template_name="groups/groups_search_results.html",
            context={"groups": groups}
        )

        data_dict = {"html_from_view": html}

        return JsonResponse(data=data_dict, safe=False)

    return render(request, "groups/groups_list_view.html", context=ctx)

# view which shows the vitals, the height and weight


@user_passes_test(patient_check, redirect_field_name='home_base')
def vitalsview(request, id):

    context = {}

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Patient.objects.get_or_create(baseuser=baseuser)[0]
    context['profile'] = profile

    # calculate yesterday's date
    yesterday = timezone.now() - timedelta(days=1)
    height = {}
    weight = {}

    try:
        height = Vital.objects.get(patient=profile, type='Height')
        context['height'] = height
    except Vital.DoesNotExist:
        pass

    try:
        # get most recent weight
        weight_list = Vital.objects.filter(
            patient=profile, type="Weight").order_by('-date')

        if weight_list:
            weight = weight_list[0]
            
        context['weight'] = weight

        # pass a context to the view which controls if the button to add your weight should be there, you should only add weight once a day.
        if Vital.objects.filter(patient=profile, type='Weight', date__gt=yesterday).exists():
            context['already'] = 'already'
    except Vital.DoesNotExist:
        pass

    # calculate the bmi from height and weight; bmi = w/h^2
    if height and weight:
        bmi = weight.value/((height.value/100)*(height.value/100))
        context['bmi'] = bmi

    response = render(request, 'vitals/weight.html', context)

    return response

# ----------------------------------file open/download----------------------------------------

# when a pdf is clicked, it is opened/downloaded in firefox


@login_required(redirect_field_name='index')
def pdf_view(request, id, pdfid):

    if id != request.user.id:
        return redirect('home_base')

    try:
        document = Document.objects.get(id=pdfid)
    except Document.DoesNotExist:
        return redirect('home_base')

    # try to find file and open it
    try:
        return FileResponse(open(MEDIA_ROOT + '/' + str(document.pdf_file), 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()

# ---------------------------------------------------------------------------------------------


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    login_url = 'accounts/login/'
    redirect_field_name = 'home_base'

    model = Document
    success_url = reverse_lazy('home_base')
    pk_url_kwarg = 'document_pk'


# a view to see all documents for a patient
@user_passes_test(patient_check, redirect_field_name='home_base')
def DocumentsView(request, id):

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Patient.objects.get_or_create(baseuser=baseuser)[0]
    context = {
        'profile': profile,
    }

    try:
        docs = Document.objects.filter(patient=profile)

        context['object_list'] = docs

    except Condition.DoesNotExist:
        pass

    response = render(request, 'documents/documents_list_view.html', context)
    return response

# a form view which allows doctors to add documents for patients


@user_passes_test(staff_check, redirect_field_name='home_base')
def DoctorDocumentCreateView(request, id, pk):

    # context user stuff
    context = {}
    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]

    try:
        groups = Group.objects.filter(members=profile)
        context['groups'] = groups
    except Group.DoesNotExist:
        pass

    try:
        tasks = Task.objects.filter(complete_by=profile, complete=False)
        context['tasks'] = tasks
    except Task.DoesNotExist:
        pass

    patient = {}
    try:
        base = CustomUser.objects.get(id=pk)
        try:
            patient = Patient.objects.get(baseuser=base)
        except Patient.DoesNotExist:
            return redirect('home_base')

    except CustomUser.DoesNotExist:
        return redirect('home_base')

    # form stuff
    form = DocDocumentForm(patient, data=request.POST or None)

    if request.method == 'POST':
        form = DocDocumentForm(patient, request.POST or None,
                               request.FILES or None)

        if form.is_valid():
            document = form.save(commit=False)
            document.added_by = profile.baseuser
            document.save()
            return redirect('patient_view', id=id,  pk=pk)
        else:
            # form = DocDocumentForm(patient, request.GET or None)
            print(form.errors)

    context['form'] = form
    context['profile'] = profile

    response = render(
        request, 'documents/document_create_view.html', context)

    return response

# loginrequiredmixin means that the user should be logged in, otherwise they cannot see the content
# a view to create documents


class DocumentCreateView(LoginRequiredMixin, CreateView):
    login_url = 'accounts/login/'
    redirect_field_name = 'home_base'

    template_name = 'documents/document_create_view.html'
    form_class = DocumentForm
    success_url = reverse_lazy('home_base')

    def get_context_data(self, **kwargs):
        context = super(DocumentCreateView,
                        self).get_context_data(**kwargs)
        profile = Patient.objects.get_or_create(
            baseuser=self.request.user)[0]
        context['profile'] = profile
        return context

    def form_valid(self, form):
        # the patient is the user, and added by the user too.
        self.obj = form.save(commit=False)
        self.obj.patient = self.request.user.patient
        self.obj.added_by = self.request.user
        self.obj.save()
        return super(DocumentCreateView, self).form_valid(form)

# similar to before


@user_passes_test(patient_check, redirect_field_name='home_base')
def ImmunizationsView(request, id):

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Patient.objects.get_or_create(baseuser=baseuser)[0]
    context = {
        'profile': profile,
    }

    try:
        immunizations = Immunization.objects.filter(patient=profile)

        context['object_list'] = immunizations

    except Condition.DoesNotExist:
        pass

    response = render(
        request, 'immunizations/immunizations_list_view.html', context)
    return response

# similar to before


@user_passes_test(patient_check, redirect_field_name='home_base')
def ConditionsView(request, id):

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Patient.objects.get_or_create(baseuser=baseuser)[0]
    context = {
        'profile': profile,
    }

    try:
        conditions = Condition.objects.filter(patient=profile)

        context['object_list'] = conditions

    except Condition.DoesNotExist:
        pass

    response = render(request, 'conditions/conditions_list_view.html', context)

    return response

# similar to before


@method_decorator(login_required, name='dispatch')
class ConditionUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'accounts/login/'
    redirect_field_name = 'home_base'

    model = Condition
    fields = ('stop', 'reaction', 'severity', 'details')
    template_name = 'conditions/condition_update_form.html'
    pk_url_kwarg = 'condition_pk'

    def get_context_data(self, **kwargs):
        context = super(ConditionUpdateView, self).get_context_data(**kwargs)
        context['condition'] = self.object
        try:
            profile = Patient.objects.get(baseuser=self.request.user)
            context['profile'] = profile
        except Patient.DoesNotExist:
            profile = Staff.objects.get(baseuser=self.request.user)
            context['profile'] = profile
        return context

    def form_valid(self, form):
        condition = form.save(commit=False)
        condition.save()
        return redirect('home_base')  # event_pk=event.id)

    def get_form(self):
        form = super().get_form()
        form.fields['stop'].widget = DatePickerInput()
        return form

# a view for a doctor to create a condition


@user_passes_test(staff_check, redirect_field_name='home_base')
def DoctorConditionCreateView(request, id, pk):

    # context stuff
    context = {}
    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]

    try:
        groups = Group.objects.filter(members=profile)
        context['groups'] = groups
    except Group.DoesNotExist:
        pass

    try:
        tasks = Task.objects.filter(complete_by=profile, complete=False)
        context['tasks'] = tasks
    except Task.DoesNotExist:
        pass

    patient = {}
    try:
        base = CustomUser.objects.get(id=pk)
        try:
            patient = Patient.objects.get(baseuser=base)
        except Patient.DoesNotExist:
            return redirect('home_base')

    except CustomUser.DoesNotExist:
        return redirect('home_base')

    # form stuff
    form = DoctorConditionForm(user=patient)

    # set form widgets
    form.fields['start'].widget = DatePickerInput()
    form.fields['stop'].widget = DatePickerInput()

    if request.method == 'POST':
        form = DoctorConditionForm(patient, request.POST)

        if form.is_valid():
            condition = form.save(commit=False)
            condition.added_by = profile.baseuser
            condition.save()
            return redirect('patient_view', id=id, pk=pk)
        else:
            # form = DoctorConditionForm(user=patient)
            print(form.errors)

    context['form'] = form
    context['profile'] = profile

    response = render(
        request, 'conditions/condition_create_view.html', context)

    return response

# similar to before


class ConditionCreateView(LoginRequiredMixin, CreateView):
    login_url = 'accounts/login/'
    redirect_field_name = 'home_base'

    template_name = 'conditions/condition_create_view.html'
    form_class = ConditionForm
    success_url = reverse_lazy('home_base')

    def get_context_data(self, **kwargs):
        context = super(ConditionCreateView,
                        self).get_context_data(**kwargs)
        profile = Patient.objects.get_or_create(
            baseuser=self.request.user)[0]
        context['profile'] = profile
        return context

    def form_valid(self, form):
        self.obj = form.save(commit=False)
        self.obj.patient = self.request.user.patient
        self.obj.added_by = self.request.user
        self.obj.save()
        return super(ConditionCreateView, self).form_valid(form)

    def get_form(self):
        form = super().get_form()
        form.fields['start'].widget = DatePickerInput()
        form.fields['stop'].widget = DatePickerInput()
        return form

# similar to before


@user_passes_test(patient_check, redirect_field_name='home_base')
def MedicationView(request, id):

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Patient.objects.get_or_create(baseuser=baseuser)[0]
    context = {
        'profile': profile,
    }

    now = date.today()

    try:
        medication = Medication.objects.filter(patient=profile)
        past = medication.filter(finish__lte=now)

        # the Q lets the queryset choose between the two constraints, so this returns medication which has a finish date in the future, or which does not have a finish date at all
        current = medication.filter(Q(finish__gt=now) | Q(finish=None))

        context['object_list'] = medication
        context['past'] = past
        context['current'] = current

    except Medication.DoesNotExist:
        pass

    response = render(request, 'medication/medication_list_view.html', context)
    return response

# view for doctor to add medication for a patient
@user_passes_test(staff_check, redirect_field_name='home_base')
def DoctorMedicationCreateView(request, id, pk):

    #context stuff
    context = {}
    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]

    try:
        groups = Group.objects.filter(members=profile)
        context['groups'] = groups
    except Group.DoesNotExist:
        pass

    try:
        tasks = Task.objects.filter(complete_by=profile, complete=False)
        context['tasks'] = tasks
    except Task.DoesNotExist:
        pass

    patient = {}
    try:
        base = CustomUser.objects.get(id=pk)
        try:
            patient = Patient.objects.get(baseuser=base)
        except Patient.DoesNotExist:
            return redirect('home_base')

    except CustomUser.DoesNotExist:
        return redirect('home_base')

    #form stuff
    form = DoctorMedicationForm(user=patient)
    form.fields['start'].widget = DatePickerInput()
    form.fields['finish'].widget = DatePickerInput()

    if request.method == 'POST':
        form = DoctorMedicationForm(patient, request.POST)

        if form.is_valid():
            # form.save()
            condition = form.save(commit=False)
            condition.added_by = profile.baseuser
            condition.save()
            return redirect('patient_view', id=id, pk=pk)
        else:
            # form = DoctorMedicationForm(user=patient)
            print(form.errors)

    context['form'] = form
    context['profile'] = profile

    response = render(
        request, 'medication/medication_create_view.html', context)

    return response

#patient can record medication
class MedicationCreateView(LoginRequiredMixin, CreateView):
    login_url = 'accounts/login/'
    redirect_field_name = 'home_base'

    template_name = 'medication/medication_create_view.html'
    form_class = MedicationForm
    success_url = reverse_lazy('home_base')

    def get_context_data(self, **kwargs):
        context = super(MedicationCreateView,
                        self).get_context_data(**kwargs)
        profile = Patient.objects.get_or_create(
            baseuser=self.request.user)[0]
        context['profile'] = profile
        return context

    def form_valid(self, form):
        self.obj = form.save(commit=False)
        self.obj.patient = self.request.user.patient
        self.obj.added_by = self.request.user
        self.obj.save()
        return super(MedicationCreateView, self).form_valid(form)

    def get_form(self):
        form = super().get_form()
        form.fields['start'].widget = DatePickerInput()
        form.fields['finish'].widget = DatePickerInput()
        return form

#when someone is done with medication they press a button and it sets the finish date to today's date. ajax.
def medication_done(request):

    #context stuff
    if request.method == 'POST':
        user = request.user
        try:
            patient = Patient.objects.get(baseuser=user)
        except Patient.DoesNotExist:
            staff = Staff.objects.get(baseuser=user)
        id = request.POST.get('id', None)
        medication = Medication.objects.get_or_create(id=id)[0]

        #actual logic
        now = date.today()

        medication.finish = now
        medication.save()
        message = 'You are no longer taking this.'

    ctx = {'message': message}
    return HttpResponse(json.dumps(ctx), content_type='application/json')

#delete a task, deleteview
class TaskDeleteView(UserPassesTestMixin, DeleteView):

    def test_func(self):
        return staff_check(self.request.user)

    model = Task

    success_url = reverse_lazy('home_base')
    pk_url_kwarg = 'task_pk'

#complete a task, ajax view, after a button press
def task_complete(request):

    if request.method == 'POST':
        user = request.user
        staff = Staff.objects.get_or_create(baseuser=user)[0]
        id = request.POST.get('id', None)
        task = Task.objects.get_or_create(id=id)[0]

        now = timezone.now()

        #task completed by specific user
        task.complete = True
        task.actually_completed = staff

        #task completed now
        task.completion_date = now
        task.save()
        message = 'You completed this'

    ctx = {'complete': staff.first_name, 'message': message}
    return HttpResponse(json.dumps(ctx), content_type='application/json')

#a view for creating a task
class TaskCreateView(UserPassesTestMixin, CreateView):
    template_name = 'task/task_create_form.html'
    form_class = TaskForm
    success_url = reverse_lazy('home_base')

    #user must be staff
    def test_func(self):
        return staff_check(self.request.user)

    #if the form is valid add 'set_by' to user
    def form_valid(self, form):
        self.obj = form.save(commit=False)
        self.obj.set_by = self.request.user.doctor
        self.obj.save()
        return super(TaskCreateView, self).form_valid(form)

    #set widget for deadline to be datetimepickerinput
    def get_form(self):
        form = super().get_form()
        form.fields['deadline'].widget = DateTimePickerInput(options={
            'minDate': ((datetime.today() + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')),
        })
        return form

    #pass relevant context data to the template
    def get_context_data(self, **kwargs):
        context = super(TaskCreateView, self).get_context_data(**kwargs)
        profile = Staff.objects.get_or_create(baseuser=self.request.user)[0]
        try:
            groups = Group.objects.filter(members=profile)
            context['groups'] = groups
        except Group.DoesNotExist:
            pass

        try:
            tasks = Task.objects.filter(complete_by=profile, complete=False)
            context['tasks'] = tasks
        except Task.DoesNotExist:
            pass
        context['profile'] = profile
        return context

#update a task if needed
class TaskUpdateView(UserPassesTestMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'task/task_update_form.html'
    pk_url_kwarg = 'task_pk'

    def test_func(self):
        return staff_check(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(TaskUpdateView, self).get_context_data(**kwargs)
        context['task'] = self.object
        profile = Staff.objects.get_or_create(
            baseuser=self.request.user)[0]
        context['profile'] = profile
        try:
            groups = Group.objects.filter(members=profile)
            context['groups'] = groups
        except Group.DoesNotExist:
            pass

        try:
            tasks = Task.objects.filter(complete_by=profile, complete=False)
            context['tasks'] = tasks
        except Task.DoesNotExist:
            pass

        return context

    def form_valid(self, form):
        task = form.save(commit=False)
        task.save()
        return redirect('task', id=self.request.user.id)

#view the search results
class PatientSearchResultsView(UserPassesTestMixin, ListView):
    model = Patient
    template_name = 'search/patient_search_results.html'
    paginate_by = 25

    def test_func(self):
        return staff_check(self.request.user)

    #pass relevant context data, as usual
    def get_context_data(self, **kwargs):
        context = super(PatientSearchResultsView,
                        self).get_context_data(**kwargs)
        profile = Staff.objects.get_or_create(
            baseuser=self.request.user)[0]
        try:
            groups = Group.objects.filter(members=profile)
            context['groups'] = groups
        except Group.DoesNotExist:
            pass

        try:
            tasks = Task.objects.filter(complete_by=profile, complete=False)
            context['tasks'] = tasks
        except Task.DoesNotExist:
            pass
        context['profile'] = profile
        return context

    #use postgres search vector to search through the database and return the object list
    def get_queryset(self):  
        query = self.request.GET.get('q', '')

        #relevant columns
        vector = SearchVector('first_name', 'last_name', 'dob', 'nhs_no')

        #only patients registered at this hospital
        relevant_patients = PatientHospital.objects.filter(
            hospital=self.request.user.doctor.ward.hospital, status=True).values('patient')
        my_patients = Patient.objects.filter(baseuser_id__in=relevant_patients)

        #actually do the search
        object_list = my_patients.annotate(search=vector).filter(search=query)

        return object_list

#pass nothing
def index(request):

    context_dict = {}
    response = render(request, 'myhealthdb/index.html', context_dict)

    return response

#pass nothing
def about(request):

    context_dict = {}
    response = render(request, 'myhealthdb/about_this.html', context_dict)

    return response

#a view for all events, such as appointments
@user_passes_test(patient_check, redirect_field_name='home_base')
def events(request, id):

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    now = timezone.now()

    profile = Patient.objects.get_or_create(baseuser=baseuser)[0]

    #separate the events based on if they are still to happen or they have happened in the past.
    new_events = Event.objects.filter(date_in__gte=now)
    past_events = Event.objects.filter(date_in__lt=now)

    context_dict = {
        'profile': profile,
        'new_events': new_events,
        'past_events': past_events,
    }
    response = render(request, 'event/events.html', context_dict)

    return response

#similar to before
class EventDeleteView(UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'event/event_delete_form.html'
    pk_url_kwarg = 'event_pk'
    success_url = reverse_lazy('task', id=id)

    def test_func(self):
        return staff_check(self.request.user)

    def get_context_data(self, **kwargs):
        context = super(EventDeleteView, self).get_context_data(**kwargs)
        context['event'] = self.object
        if self.request.user.user_type == 1:
            profile = Patient.objects.get_or_create(
                baseuser=self.request.user)[0]
        else:
            profile = Staff.objects.get_or_create(
                baseuser=self.request.user)[0]
        context['profile'] = profile
        return context

#similar to before
@method_decorator(login_required, name='dispatch')
class EventUpdateView(LoginRequiredMixin, UpdateView):
    login_url = 'accounts/login/'
    redirect_field_name = 'home_base'

    model = Event
    fields = ('title', 'date_in', 'notes')
    template_name = 'event/event_update_form.html'
    pk_url_kwarg = 'event_pk'

    def get_context_data(self, **kwargs):
        context = super(EventUpdateView, self).get_context_data(**kwargs)
        context['event'] = self.object
        if self.request.user.user_type == 1:
            profile = Patient.objects.get_or_create(
                baseuser=self.request.user)[0]
        else:
            profile = Staff.objects.get_or_create(
                baseuser=self.request.user)[0]
        context['profile'] = profile
        return context

    def form_valid(self, form):
        event = form.save(commit=False)
        event.save()
        return redirect('home_base') 

    def get_form(self):
        form = super().get_form()
        form.fields['date_in'].widget = DateTimePickerInput(options={
            'minDate': (datetime.datetime.today()).strftime('%Y-%m-%d %H:%M:%S'),
            'enabledHours': [8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
        })
        return form

#staff can create an event too
@user_passes_test(staff_check, redirect_field_name='home_base')
def staff_event_create(request, id):

    #context stuff
    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Staff.objects.get(baseuser=baseuser)

    form = StaffEventBookingForm(profile.ward.hospital)
    form.fields['date_in'].widget = DateTimePickerInput(options={
        #min time is not, so cannot create it in the past
        'minDate': ((datetime.today() - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')),
    })

    #form stuff
    if request.method == 'POST':
        form = StaffEventBookingForm(
            profile.ward.hospital, request.POST or None)

        if form.is_valid():
            newevent = form.save(commit=False)
            newevent.save()
            return redirect('home_base')
        else:
            # form = StaffEventBookingForm(
            #     profile.ward.hospital, request.GET or None)
            print(form.errors)

    context = {
        'form': form,
        'profile': profile,
    }

    response = render(request, 'event/event_create_form.html', context)

    return response

#patient event create
@user_passes_test(patient_check, redirect_field_name='home_base')
def event_create(request, id):

    #context stuff
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

    #form stuff
    form = EventBookingForm(user=profile)
    form.fields['date_in'].widget = DateTimePickerInput(options={
        'minDate': ((datetime.today()).strftime('%Y-%m-%d %H:%M:%S')),
        'maxDate': ((datetime.today() + timedelta(days=7)).strftime('%Y-%m-%d 23:59:59')),

        #patient can only book in opening times
        'enabledHours': [9, 10, 11, 12, 13, 14, 15, 16],
    })

    if request.method == 'POST':
        form = EventBookingForm(profile, request.POST)

        if form.is_valid():
            newevent = form.save(commit=False)
            newevent.save()
            return redirect('home_base')
        else:
            # form = EventBookingForm(user=profile)
            print(form.errors)

    context = {
        'form': form,
        'profile': profile,
    }

    response = render(request, 'event/event_create_form.html', context)

    return response

#passing values to patient_home
@user_passes_test(patient_check, redirect_field_name='home_base')
def patient_home(request, id):

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Patient.objects.get_or_create(baseuser=baseuser)[0]
    context = {
        'profile': profile,
    }
    try:
        #get all relevant events by accumulating the hospital registrations the patient has
        pdrelations = PatientHospital.objects.filter(
            patient=profile, status=True)
        context['pdrelations'] = pdrelations
        events = Event.objects.filter(
            pd_relation__in=pdrelations, date_in__gte=timezone.now())
        context['events'] = events

    except PatientHospital.DoesNotExist:
        pass

    response = render(request, 'myhealthdb/patient/patient_home.html', context)

    return response

#staff home has a lot of data to be passed since there are 3 types of staff with all different data needs
@user_passes_test(staff_check, redirect_field_name='home_base')
def staff_home(request, id):

    context = {
    }

    now = date.today()
    last_monday = now - timedelta(days=now.weekday())
    next_monday = last_monday + timedelta(days=6)

    #get the days of the current week for the it guy table
    dates = []
    dates.append(last_monday)
    for i in range(1, 7):
        next = last_monday + timedelta(days=i)
        dates.append(next)

    context['dates'] = dates

    #get the current user
    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]
    context['profile'] = profile

    #pass groups and tasks in the side bar
    try:
        groups = Group.objects.filter(members=profile)
        context['groups'] = groups
    except Group.DoesNotExist:
        pass

    try:
        tasks = Task.objects.filter(complete_by=profile, complete=False)
        context['tasks'] = tasks
    except Task.DoesNotExist:
        pass

    #if staff is a doctor, we pass events and inpatients
    if profile.baseuser.user_type == 2:
        try:
            pdrelations = PatientHospital.objects.filter(
                hospital=profile.ward.hospital, status=True)

            try:
                events = Event.objects.filter(
                    pd_relation__in=pdrelations, date_in__date=date.today())
                context['events'] = events
            except Event.DoesNotExist:
                pass

            try:
                ph = PatientHospital.objects.filter(
                    inpatient=True, hospital=profile.ward.hospital).values('patient')
                inpatients = Patient.objects.filter(baseuser__in=ph)
                context['inpatients'] = inpatients
            except PatientHospital.DoesNotExist:
                pass

        except PatientHospital.DoesNotExist:
            pass

    #if staff is receptionist, we pass events and pending registrations
    elif profile.baseuser.user_type == 3:
        try:
            pdrelations = PatientHospital.objects.filter(
                hospital=profile.ward.hospital, status=True)
            try:
                events = Event.objects.filter(date_in__date=date.today())
                events = events.filter(pd_relation__in=pdrelations)
                context['events'] = events
            except Event.DoesNotExist:
                pass
        except PatientHospital.DoesNotExist:
            pass

        try:
            pending = PatientHospital.objects.filter(
                hospital=profile.ward.hospital, status=False)
            context['pending'] = pending
        except PatientHospital.DoesNotExist:
            pass

    #if staff is itguy, we pass events and the schedule for staff with shifts
    elif profile.baseuser.user_type == 4:

        staff = {}
        events = {}
        try:
            staff = Staff.objects.filter(ward=profile.ward)
            context['staff'] = staff
            try:
                events = Shift.objects.filter(staff__in=staff)
                context['events'] = events
            except Shift.DoesNotExist():
                pass
        except Staff.DoesNotExist():
            pass

        schedule = []
        for i in range(0, len(staff)):

            schedule.append(staff[i])
            for j in range(0, len(dates)):
                for k in range(0, len(events)):
                    if events[k].date == dates[j] and events[k].staff == staff[i]:
                        schedule.append(events[k])
                        break
                    elif k == len(events)-1:
                        schedule.append(None)

        context['schedule'] = schedule

    response = render(request, 'myhealthdb/staff/staff_home.html', context)

    return response

#patient looks at own details
@user_passes_test(patient_check, redirect_field_name='home_base')
def patient_details(request, id):

    context = {}

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Patient.objects.get_or_create(baseuser=baseuser)[0]

    context['profile'] = profile

    #change the address format so geopy can work out the text address from the coordinates
    prev_address = profile.address
    prev_address = prev_address[7:-1]
    splits = prev_address.split(" ")
    prev_address = prev_address.replace(" ", ",")
    swap_address = prev_address.split(",")
    h_address = swap_address[1] + "," + swap_address[0]
    new_address = geolocator.reverse(h_address, exactly_one=True)
    context['new_address'] = new_address

    try:
        pem = PatientEm.objects.filter(patient=profile)
        context['pem'] = pem
    except PatientEm.DoesNotExist:
        pass

    response = render(
        request, 'myhealthdb/patient/patient_details.html', context)
    return response

#form for patient to update her details
@user_passes_test(patient_check, redirect_field_name='home_base')
def patient_details_update(request, id):

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Patient.objects.get_or_create(baseuser=baseuser)[0]

    #form stuff, there is a form and a formset, both get passed as post data and saved.
    form = PatientProfileForm({'dob': profile.dob, 'first_name': profile.first_name, 'last_name': profile.last_name, 'sex': profile.sex, 'tel_no': profile.tel_no, 'nhs_no': profile.nhs_no,
                               'address': profile.address}) 
    form.fields['dob'].widget = DatePickerInput()
    form.fields['address'].widget = GooglePointFieldWidget()
    ecformset = ECSet(instance=request.user.patient)

    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=request.user.patient)
        ecformset = ECSet(request.POST or None,
                          request.FILES or None, instance=request.user.patient)

        if form.is_valid() and ecformset.is_valid():
            profile = form.save(commit=False)
            profile.save()

            ecformset.save()

            return redirect('patient_home', id)

        else:
            # form = PatientProfileForm(instance=request.user.patient)
            # ecformset = ECSet(request.GET or None,
            #                   instance=request.user.patient)
            print(form.errors)

    context = {
        'form': form,
        'ecformset': ecformset,
        'profile': profile,
    }

    response = render(
        request, 'myhealthdb/patient/patient_details_update.html', context)
    return response

#displays all the tasks for the staff
@user_passes_test(staff_check, redirect_field_name='home_base')
def task_home(request, id):

    context = {}

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    now = timezone.now()

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]

    #separate the tasks into: my tasks, i.e. tasks i have to complete, and tasks by me, i.e tasks i have set. 
    #further separate them into 3 categories each, due, overdue, and finished.

    my_tasks_overdue = Task.objects.filter(
        complete=False, complete_by=profile, deadline__lte=now)
    my_tasks_due = Task.objects.filter(
        complete=False, complete_by=profile, deadline__gte=now)
    my_tasks_finished = Task.objects.filter(complete_by=profile, complete=True)

    tasks_by_me_overdue = Task.objects.filter(
        complete=False, set_by=profile, deadline__lte=now)
    tasks_by_me_due = Task.objects.filter(
        complete=False, set_by=profile, deadline__gte=now)
    tasks_by_me_finished = Task.objects.filter(set_by=profile, complete=True)

    try:
        groups = Group.objects.filter(members=profile)
        context['groups'] = groups
    except Group.DoesNotExist:
        pass

    try:
        tasks = Task.objects.filter(complete_by=profile, complete=False)
        context['tasks'] = tasks
    except Task.DoesNotExist:
        pass

    #pass everything to context
    context['profile'] = profile
    context['my_tasks_overdue'] = my_tasks_overdue
    context['my_tasks_due'] = my_tasks_due
    context['my_tasks_finished'] = my_tasks_finished
    context['tasks_by_me_overdue'] = tasks_by_me_overdue
    context['tasks_by_me_due'] = tasks_by_me_due
    context['tasks_by_me_finished'] = tasks_by_me_finished

    response = render(request, 'task/tasks.html', context)
    return response

#staff details is a form, prepopulated
@user_passes_test(staff_check, redirect_field_name='home_base')
def staff_details(request, id):
    
    #context stuff
    context = {}

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]

    #we prefill the fields of the form
    form = StaffProfileForm({'tel_no': profile.tel_no, 'first_name': profile.first_name,
                             'last_name': profile.last_name})  # , 'ward': profile.ward

    try:
        groups = Group.objects.filter(members=profile)
        context['groups'] = groups
    except Group.DoesNotExist:
        pass

    try:
        tasks = Task.objects.filter(complete_by=profile, complete=False)
        context['tasks'] = tasks
    except Task.DoesNotExist:
        pass

    #form stuff
    if request.method == 'POST':
        form = StaffProfileForm(request.POST, instance=request.user.doctor)

        if form.is_valid():
            profile = form.save(commit=False)
            profile.save()
            return redirect('staff_home', id)
        else:
            # form = StaffProfileForm(instance=request.user.doctor)
            print(form.errors)

    context['form'] = form
    context['profile'] = profile

    response = render(request, 'myhealthdb/staff/staff_details.html', context)
    return response

#home base is the view the redirects requests depending on who the user is. if he is a patient, we redirect to patient_home etc
@login_required(redirect_field_name='index')
def home_base(request):

    thisid = request.user.id
    if thisid == None:
        return redirect('index')

    if request.user.is_superuser:
        return redirect('admin:index')

    if request.user.user_type == 1:
        return redirect('patient_home', id=thisid)
    else:
        return redirect("staff_home", id=thisid)
