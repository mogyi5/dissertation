from django.shortcuts import render, redirect, get_object_or_404
from allauth.account.views import SignupView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from myhealthdb.forms import EventFormSet, CustomUserForm, StaffSignupForm, TaskForm, PatientSignupForm, PatientProfileForm, StaffProfileForm, HospitalContactForm, ECSet,  EventBookingForm, MedicationForm, ConditionForm, DocumentForm  # PDSet,
from myhealthdb.models import Shift, Task, Ward, CustomUser, Patient, Staff, PatientEm, Event, Group, Medication, Condition, Immunization, Document, Weight, PatientHospital, Hospital  # PatientDoctor,
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
from bootstrap_modal_forms.generic import BSModalCreateView
from django.http import HttpResponse, HttpResponseRedirect, FileResponse, Http404, JsonResponse
try:
    from django.utils import simplejson as json
except ImportError:
    import json
from myhealthdb_project.settings import MEDIA_ROOT, MEDIA_URL
from chartjs.views.lines import BaseLineChartView
from chartjs.util import date_range, value_or_null
from django.template.loader import render_to_string, get_template
from mapwidgets.widgets import GooglePointFieldWidget
from django.contrib.gis import gdal
from geopy.geocoders import Nominatim, GoogleV3
from geopy import distance
from math import sin, cos, sqrt, atan2, radians


geolocator = GoogleV3(api_key="AIzaSyCzCYVvHq7yit0ESbH-OLn8r0dA4WiMb8I")


def patient_check(user):
    if user.user_type == 1:
        return True
    return False


def staff_check(user):
    if user.user_type == 2 or user.user_type == 3 or user.user_type == 4:
        return True
    return False


def request_user_check(user):
    if id == request.user.id:
        return True
    return False


# Create your views here.


def patient_view(request, id, pk):
    context = {}

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]
    context['profile'] = profile

    patient = {}
    pathospitals = PatientHospital.objects.filter(
        hospital=profile.ward.hospital).values('patient')[0]


    try:
        patient = Patient.objects.get(baseuser_id=pk)

        if patient.baseuser_id == pathospitals['patient']:
            context['patient'] = patient
            context['patientem'] = PatientEm.objects.filter(patient = patient)
            context['conditions'] = Condition.objects.filter(patient = patient)
            context['medications'] = Medication.objects.filter(patient = patient)
            context['immunizations'] = Immunization.objects.filter(patient = patient)
            context['documents'] = Document.objects.filter(patient = patient)
        else:
            pass

    except Patient.DoesNotExist:

        return redirect('home_base')

    response = render(request, 'search/patient_details.html', context)

    return response


class ShiftDeleteView(DeleteView):
    model = Shift
    template_name = "admin_things/shift_delete_view.html"
    success_url = reverse_lazy('home_base')

    def get_context_data(self, **kwargs):
        context = super(ShiftDeleteView, self).get_context_data(**kwargs)
        profile = Staff.objects.get_or_create(
            baseuser=self.request.user)[0]
        context['profile'] = profile
        return context


class ShiftUpdateView(UpdateView):
    model = Shift
    fields = ('start', 'end', 'date', 'staff')
    template_name = 'admin_things/shift_update_form.html'
    success_url = reverse_lazy('home_base')
    # pk_url_kwarg = 'condition_pk'
    # context_object_name = 'event'

    # def get_queryset(self):
    #     return CustomUser.objects.filter(id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super(ShiftUpdateView, self).get_context_data(**kwargs)
        context['shift'] = self.object
        profile = Staff.objects.get_or_create(
            baseuser=self.request.user)[0]
        context['profile'] = profile
        return context

    # def form_valid(self, form):
    #     condition = form.save(commit=False)
    #     condition.save()
    #     return redirect('home_base')  # event_pk=event.id)

    def get_form(self):
        form = super().get_form()
        form.fields['date'].widget = DatePickerInput()
        form.fields['start'].widget = TimePickerInput()
        form.fields['end'].widget = TimePickerInput()
        return form


# needs to be it guy
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

    efformset = EventFormSet(prefix="foo",)

    if request.method == 'POST':
        efformset = EventFormSet(request.POST or None,
                                 request.FILES or None, prefix="foo")

        if efformset.is_valid():

            for f in efformset:
                f.save()

            # efformset.save()

            return HttpResponseRedirect(reverse_lazy('home_base'))

        else:
            efformset = EventFormSet(request.GET or None, prefix="foo")
            # print(form.errors)

    context['efformset'] = efformset

    response = render(request, 'admin_things/schedule_create.html', context)

    return response


class StaffDeleteView(DeleteView):
    model = Staff
    template_name = "admin_things/staff_delete_view.html"
    success_url = reverse_lazy('home_base')

    def get_context_data(self, **kwargs):
        context = super(StaffDeleteView, self).get_context_data(**kwargs)
        profile = Staff.objects.get_or_create(
            baseuser=self.request.user)[0]
        context['profile'] = profile
        return context


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
            # form.save()

            return redirect('home_base')

        else:
            form = StaffSignupForm(request.GET or None)
            baseform = CustomUserForm(request.GET or None)

    baseform.auto_id = True

    context['form'] = form
    context['baseform'] = baseform

    response = render(request, 'admin_things/staff_create_form.html', context)

    return response


# class StaffCreateView(CreateView):
#     template_name = 'admin_things/staff_create_form.html'
#     form_class = StaffSignupForm
#     success_url = reverse_lazy('home_base')

#     def get_context_data(self, **kwargs):
#         context = super(StaffCreateView, self).get_context_data(**kwargs)
#         profile = Staff.objects.get_or_create(baseuser=self.request.user)[0]
#         context['profile'] = profile
#         return context


# need to be it guy!
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
    totalwards = wards.count()
    context['totalwards'] = totalwards

    individualstaff = wards.annotate(
        staffnumber=Count('current_ward')).values()
    context['individualstaff'] = individualstaff
    totalstaff = individualstaff.aggregate(Sum('staffnumber'))
    context['totalstaff'] = totalstaff

    staff = Staff.objects.filter(ward__in=wards)

    context['staff'] = staff

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


class PatientView(ListView):
    model = Patient
    template_name = "search/patient_view.html"
    #paginate_by = 10

    def get_queryset(self):
        hospital = Hospital.objects.get(
            name=self.request.user.doctor.ward.hospital.name)
        patienthospitals = PatientHospital.objects.filter(
            hospital=hospital, status=True).values('patient')
        if patienthospitals:
            new_context = Patient.objects.filter(
                baseuser_id__in=patienthospitals).order_by('last_name')
        else:
            new_context = {}
        return new_context

    def get_context_data(self, **kwargs):
        context = super(PatientView, self).get_context_data(**kwargs)
        profile = Staff.objects.get_or_create(
            baseuser=self.request.user)[0]
        context['profile'] = profile
        return context


def reject_patient(request):

    if request.method == 'POST':
        # user = request.user
        # patient = Patient.objects.get_or_create(baseuser=user)[0]
        id = request.POST.get('id', None)
        patienthospital = PatientHospital.objects.get_or_create(id=id)[0]

        patienthospital.delete()
        message = 'The patient has been rejected'
        # exists = False
        # try:
        #     existing = PatientHospital.objects.get(id=id)
        #     exists = True
        # except PatientHospital.DoesNotExist:
        #     pass

        # if exists:
        #     message = 'You are already registered with this hospital.'
        # else:
        # ph = PatientHospital(patient=patient, hospital=hospital)
        # ph.save()
        # message = 'You have sent your details to the practice.'

    ctx = {'message': message}
    # use mimetype instead of content_type if django < 5
    return HttpResponse(json.dumps(ctx), content_type='application/json')


def accept_patient(request):

    if request.method == 'POST':
        # user = request.user
        # patient = Patient.objects.get_or_create(baseuser=user)[0]
        id = request.POST.get('id', None)
        patienthospital = PatientHospital.objects.get_or_create(id=id)[0]

        patienthospital.status = True
        patienthospital.save()
        message = 'The patient has been registered'
        # exists = False
        # try:
        #     existing = PatientHospital.objects.get(id=id)
        #     exists = True
        # except PatientHospital.DoesNotExist:
        #     pass

        # if exists:
        #     message = 'You are already registered with this hospital.'
        # else:
        # ph = PatientHospital(patient=patient, hospital=hospital)
        # ph.save()
        # message = 'You have sent your details to the practice.'

    ctx = {'message': message}
    # use mimetype instead of content_type if django < 5
    return HttpResponse(json.dumps(ctx), content_type='application/json')


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
            message = 'You are already registered with this hospital.'
        else:
            ph = PatientHospital(patient=patient, hospital=hospital)
            ph.save()
            message = 'You have sent your details to the practice.'

    ctx = {'message': message}
    # use mimetype instead of content_type if django < 5
    return HttpResponse(json.dumps(ctx), content_type='application/json')


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

    try:
        pending_hosp = PatientHospital.objects.filter(
            patient=profile, status=False).values('hospital')
        r_pending = Hospital.objects.filter(id__in=pending_hosp)
        context['r_pending'] = r_pending
    except PatientHospital.DoesNotExist:
        pass

    try:
        confirmed_hosp = PatientHospital.objects.filter(
            patient=profile, status=True).values('hospital')
        r_confirmed = Hospital.objects.filter(id__in=confirmed_hosp)
        context['r_confirmed'] = r_confirmed
    except PatientHospital.DoesNotExist:
        pass

    # try:
    #     hospitalrelations = PatientHospital.objects.filter(patient=profile)
    #     context['hospitalrelations'] = hospitalrelations
    # except PatientHospital.DoesNotExist:
    #     pass

    # try:
    #     pdrelations = PatientDoctor.objects.get(patient=profile)
    #     events = pdrelations.reversepd.filter(date_in__gte=timezone.now())

    #     context['events'] = events

    # except PatientDoctor.DoesNotExist:
    #     pass

    response = render(request, 'doctors_reg/doctors_view.html', context)

    return response


def distance2(lat0, long0, lat1, long1):
    rad = 6373.0

    longitude_dist = long1-long0
    latitude_dist = lat1-lat0

    a = sin(latitude_dist / 2)**2 + cos(lat0) * \
        cos(lat1) * sin(longitude_dist / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    dist = c*rad
    return dist


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

    profileaddress = profile.address
    profilecutaddress = profileaddress[7:-1]
    profilecutaddress = profilecutaddress.replace(" ", ",")
    location = geolocator.reverse(profilecutaddress)

    openhospitals = Hospital.objects.filter(taking_patients=True)

    closest = []
    largest = 0
    largestmember = ''
    maxim = 5
    for i in range(0, len(openhospitals)):

        data_array = {}
        address = openhospitals[i].address
        cutaddress = address[7:-1]
        print(cutaddress)
        cutaddress = cutaddress.replace(" ", ",")
        print(cutaddress)

        thedistance = distance.distance(
            profilecutaddress, cutaddress).miles  # change from km to miles
        data_array[0] = openhospitals[i]
        # for_display = str(thedistance)[0:3]
        data_array[1] = thedistance

        if closest:
            for k in range(0, len(closest)):
                if len(closest) < maxim:
                    if thedistance <= closest[k][1] or len(closest) < maxim:
                        closest.insert(k+1, data_array)
                        break
                else:
                    if thedistance <= closest[k][1]:
                        print('too big')
                        closest.insert(k+1, data_array)
                        del closest[k]
                        break
        else:
            closest.append(data_array)
    context['closest'] = closest

    # pdformset = PDSet(instance=request.user.patient)

    # if request.method == 'POST':
    #     pdformset = PDSet(request.POST or None,
    #                       request.FILES or None, instance=request.user.patient)

    #     if pdformset.is_valid():

    #         pdformset.save()

    #         return redirect('home_base')

    #     else:
    #         pdformset = PDSet(request.GET or None,
    #                           instance=request.user.patient)
    #         # print(form.errors)

    # context['pdformset'] = pdformset

    response = render(request, 'doctors_reg/doctors_reg.html', context)

    return response


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


# class GroupsListView(ListView):
#     model = Group
#     template_name = 'groups/groups_list_view.html'
#     paginate_by = 25

#     def get_context_data(self, **kwargs):
#         context = super(GroupsListView,
#                         self).get_context_data(**kwargs)
#         profile = Staff.objects.get_or_create(
#             baseuser=self.request.user)[0]
#         context['profile'] = profile
#         return context

class WeightChartJSONView(BaseLineChartView):
    def get_labels(self):
        """Return 7 labels for the x-axis."""
        return ["January", "February", "March", "April", "May", "June", "July"]

    def get_providers(self):
        """Return names of datasets."""
        return ["Central", "Eastside", "Westside"]

    def get_data(self):
        """Return 3 datasets to plot."""
        return [[75, 44, 92, 11, 44, 95, 35],
                [41, 92, 18, 3, 73, 87, 92],
                [87, 21, 94, 3, 90, 13, 65]]

    # def get_options(self):
    #     options = {
    #         "elements": {
    #             "point": {
    #                 "pointStyle": "rectRounded",
    #                 "radius": 10,
    #             },
    #         },
    #         "scales": {
    #             "xAxes": [{
    #                 "display":'true',
    #                 "type": 'time',
    #                 "distribution": 'series'
    #             }]
    #         },
    #         'responsive': 'True',
    #     }
    #     return options


line_chart = TemplateView.as_view(template_name='line_chart.html')
line_chart_json = WeightChartJSONView.as_view()


# class WeightChartJSON2View(BaseLineChartView):
#     start_date = Weight.objects.earliest('date').date
#     end_date = Weight.objects.latest('date').date
#     print(end_date)

#     def get_providers(self):
#         return ["Weight"]

#     def get_labels(self):
#         return [dt for dt in date_range(self.start_date, self.end_date)]

#     def get_data(self):
#         result = []
#         weight = Weight.objects.all()
#         data = [item for item in value_or_null(self.start_date, self.end_date, weight, "date", "value")]
#         result.append(data)
#         return result

# line_chart_json2 = WeightChartJSON2View.as_view()


@user_passes_test(patient_check, redirect_field_name='home_base')
def weightview(request, id):

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
    # try:
    #     pdrelations = PatientDoctor.objects.get(patient=profile)
    #     events = pdrelations.reversepd.filter(date_in__gte=timezone.now())

    #     context['events'] = events

    # except PatientDoctor.DoesNotExist:
    #     pass

    response = render(request, 'vitals/weight.html', context)

    return response

# ----------------------------------file open/download----------------------------------------


# fixfixfix
def pdf_view(request, id, pdfid):

    if id != request.user.id:
        return redirect('home_base')

    try:
        document = Document.objects.get(id=pdfid)
    except Document.DoesNotExist:
        return redirect('home_base')
    print(str(document.file))

    try:
        return FileResponse(open(MEDIA_ROOT + '/' + str(document.file), 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise Http404()


# ---------------------------------------------------------------------------------------------

class DocumentDeleteView(DeleteView):
    model = Document
    # success_url = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    success_url = reverse_lazy('home_base')
    pk_url_kwarg = 'document_pk'


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


class DocumentCreateView(CreateView):
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
        self.obj = form.save(commit=False)
        self.obj.patient = self.request.user.patient
        self.obj.save()
        return super(DocumentCreateView, self).form_valid(form)


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


@method_decorator(login_required, name='dispatch')
class ConditionUpdateView(UpdateView):
    model = Condition
    fields = ('stop', 'reaction', 'severity', 'details')
    template_name = 'conditions/condition_update_form.html'
    pk_url_kwarg = 'condition_pk'
    # context_object_name = 'event'

    # def get_queryset(self):
    #     return CustomUser.objects.filter(id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super(ConditionUpdateView, self).get_context_data(**kwargs)
        context['condition'] = self.object
        profile = Patient.objects.get_or_create(
            baseuser=self.request.user)[0]
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


class ConditionCreateView(CreateView):
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
        self.obj.save()
        return super(ConditionCreateView, self).form_valid(form)

    def get_form(self):
        form = super().get_form()
        form.fields['start'].widget = DatePickerInput()
        form.fields['stop'].widget = DatePickerInput()
        return form


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
        current = medication.filter(finish__gt=now)

        context['object_list'] = medication
        context['past'] = past
        context['current'] = current

    except Medication.DoesNotExist:
        pass

    response = render(request, 'medication/medication_list_view.html', context)
    return response

    # model = Medication
    # template_name = 'medication/medication_list_view.html'
    # paginate_by = 20

    # def get_context_data(self, **kwargs):
    #     context = super(MedicationView,
    #                     self).get_context_data(**kwargs)
    #     profile = Patient.objects.get_or_create(
    #         baseuser=self.request.user)[0]
    #     context['profile'] = profile
    #     return context


class MedicationCreateView(CreateView):
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
        self.obj.save()
        return super(MedicationCreateView, self).form_valid(form)

    def get_form(self):
        form = super().get_form()
        form.fields['start'].widget = DatePickerInput()
        form.fields['finish'].widget = DatePickerInput()
        return form


def medication_done(request):

    if request.method == 'POST':
        user = request.user
        patient = Patient.objects.get_or_create(baseuser=user)[0]
        id = request.POST.get('id', None)
        medication = Medication.objects.get_or_create(id=id)[0]

        now = date.today()

        # medicine has been stopped
        medication.finish = now
        medication.save()
        message = 'You are no longer taking this.'

    ctx = {'message': message}
    # use mimetype instead of content_type if django < 5
    return HttpResponse(json.dumps(ctx), content_type='application/json')

    # return redirect('home_base')

    # def get_queryset(self):  # new
    #     query = self.request.GET.get('q', '')

    #     vector = SearchVector('first_name', 'last_name')

    #     my_patients = Patient.objects.all()  # have this not all()
    #     object_list = my_patients.annotate(search=vector).filter(search=query)

    # Patient.objects.filter(SearchVector('first_name', 'last_name') = query)
    # object_list = Patient.objects.filter(
    #     Q(first_name__icontains=query) | Q(last_name__icontains=query)
    # )
    # return object_list


class TaskDeleteView(DeleteView):
    model = Task
    # success_url = HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    success_url = reverse_lazy('home_base')
    pk_url_kwarg = 'task_pk'

    # def get_context_data(self, **kwargs):
    #     context = super(EventDeleteView, self).get_context_data(**kwargs)
    #     context['event'] = self.object
    #     if self.request.user.user_type == 1:
    #         profile = Patient.objects.get_or_create(
    #             baseuser=self.request.user)[0]
    #     else:
    #         profile = Staff.objects.get_or_create(
    #             baseuser=self.request.user)[0]
    #     context['profile'] = profile
    #     return context


def task_complete(request):

    if request.method == 'POST':
        user = request.user
        staff = Staff.objects.get_or_create(baseuser=user)[0]
        id = request.POST.get('id', None)
        task = Task.objects.get_or_create(id=id)[0]

        now = timezone.now()

        # task completed by specific user
        task.complete = True
        task.actually_completed = staff
        task.completion_date = now
        task.save()
        message = 'You completed this'

    ctx = {'complete': staff.first_name, 'message': message}
    # use mimetype instead of content_type if django < 5
    return HttpResponse(json.dumps(ctx), content_type='application/json')


class TaskCreateView(CreateView):
    template_name = 'task/task_create_form.html'
    form_class = TaskForm
    success_url = reverse_lazy('home_base')

    def form_valid(self, form):
        self.obj = form.save(commit=False)
        self.obj.set_by = self.request.user.doctor
        self.obj.save()

        return super(TaskCreateView, self).form_valid(form)

    def get_form(self):
        form = super().get_form()
        form.fields['deadline'].widget = DateTimePickerInput(options={
            'minDate': ((datetime.today() + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')),
        })
        return form

    def get_context_data(self, **kwargs):
        context = super(TaskCreateView, self).get_context_data(**kwargs)
        profile = Staff.objects.get_or_create(baseuser=self.request.user)[0]
        context['profile'] = profile
        return context


@method_decorator(login_required, name='dispatch')
class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'task/task_update_form.html'
    pk_url_kwarg = 'task_pk'
    # context_object_name = 'event'

    # def get_queryset(self):
    #     return CustomUser.objects.filter(id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super(TaskUpdateView, self).get_context_data(**kwargs)
        context['task'] = self.object
        profile = Staff.objects.get_or_create(
            baseuser=self.request.user)[0]
        context['profile'] = profile
        return context

    def form_valid(self, form):
        task = form.save(commit=False)
        task.save()
        return redirect('home_base')


# @user_passes_test(staff_check, redirect_field_name='home_base') ##add these ok
class PatientSearchResultsView(ListView):
    model = Patient
    template_name = 'search/patient_search_results.html'
    paginate_by = 25

    def get_context_data(self, **kwargs):
        context = super(PatientSearchResultsView,
                        self).get_context_data(**kwargs)
        profile = Staff.objects.get_or_create(
            baseuser=self.request.user)[0]
        context['profile'] = profile
        return context

    def get_queryset(self):  # new
        query = self.request.GET.get('q', '')

        vector = SearchVector('first_name', 'last_name', 'dob', 'nhs_no')

        relevant_patients = PatientHospital.objects.filter(
            hospital=self.request.user.doctor.ward.hospital).values('patient')
        my_patients = Patient.objects.filter(baseuser_id__in=relevant_patients)
        object_list = my_patients.annotate(search=vector).filter(search=query)

        # Patient.objects.filter(SearchVector('first_name', 'last_name') = query)
        # object_list = Patient.objects.filter(
        #     Q(first_name__icontains=query) | Q(last_name__icontains=query)
        # )
        return object_list


def index(request):

    context_dict = {}
    response = render(request, 'myhealthdb/index.html', context_dict)

    return response


def about(request):

    context_dict = {}
    response = render(request, 'myhealthdb/about_this.html', context_dict)

    return response


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

    new_events = Event.objects.filter(date_in__gte=now)
    past_events = Event.objects.filter(date_in__lte=now)

    context_dict = {
        'profile': profile,
        'new_events': new_events,
        'past_events': past_events,
    }
    response = render(request, 'event/events.html', context_dict)

    return response


class EventDeleteView(DeleteView):
    model = Event
    template_name = 'event/event_delete_form.html'
    pk_url_kwarg = 'event_pk'
    success_url = reverse_lazy('home_base')

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


@method_decorator(login_required, name='dispatch')
class EventUpdateView(UpdateView):
    model = Event
    fields = ('letter', 'date_in', 'pd_relation', 'notes', 'done')
    template_name = 'event/event_update_form.html'
    pk_url_kwarg = 'event_pk'
    # context_object_name = 'event'

    # def get_queryset(self):
    #     return CustomUser.objects.filter(id=self.request.user.id)

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
        # event.updated_by = self.request.profile
        event.save()
        return redirect('home_base')  # event_pk=event.id)

    def get_form(self):
        form = super().get_form()
        form.fields['date_in'].widget = DateTimePickerInput()
        return form


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
    form.fields['date_in'].widget = DateTimePickerInput(options={
        'minDate': ((datetime.today() - timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')),
        'maxDate': ((datetime.today() + timedelta(days=7)).strftime('%Y-%m-%d 23:59:59'))
    })

    if request.method == 'POST':
        form = EventBookingForm(request.POST)

        if form.is_valid():
            # form.save()
            newevent = form.save(commit=False)
            newevent.save()
            return redirect('home_base')
        else:
            form = EventBookingForm()
            print(form.errors)

    context = {
        'form': form,
        'profile': profile,
    }

    response = render(request, 'event/event_create_form.html', context)

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
    context = {
        'profile': profile,
    }
    try:
        pdrelations = PatientHospital.objects.filter(patient=profile)
        events = Event.objects.filter(
            pd_relation__in=pdrelations, date_in__gte=timezone.now())

        context['events'] = events

    except PatientHospital.DoesNotExist:
        pass

    response = render(request, 'myhealthdb/patient/patient_home.html', context)

    return response


@user_passes_test(staff_check, redirect_field_name='home_base')
def staff_home(request, id):

    context = {
    }

    now = date.today()
    last_monday = now - timedelta(days=now.weekday())
    next_monday = last_monday + timedelta(days=6)

    dates = []
    dates.append(last_monday)
    for i in range(1, 7):
        next = last_monday + timedelta(days=i)
        dates.append(next)

    context['dates'] = dates  # DISPLAY THIS

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]
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

    if profile.baseuser.user_type == 2:
        try:
            pdrelations = PatientHospital.objects.filter(
                hospital=profile.ward.hospital)

            try:
                events = Event.objects.filter(
                    pd_relation__in=pdrelations, date_in__date=date.today())
                context['events'] = events
            except Event.DoesNotExist:
                pass

            try:
                inpatients = PatientHospital.objects.filter(
                    inpatient=True, hospital=profile.ward.hospital)
                context['inpatients'] = inpatients
            except PatientHospital.DoesNotExist:
                pass

        except PatientHospital.DoesNotExist:
            pass

    elif profile.baseuser.user_type == 3:
        try:
            pdrelations = PatientHospital.objects.filter(
                hospital=profile.ward.hospital)
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

#################################################################################################################################


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


@user_passes_test(patient_check, redirect_field_name='home_base')
def patient_details_update(request, id):

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Patient.objects.get_or_create(baseuser=baseuser)[0]
    form = PatientProfileForm({'dob': profile.dob, 'first_name': profile.first_name, 'last_name': profile.last_name, 'sex': profile.sex, 'tel_no': profile.tel_no, 'nhs_no': profile.nhs_no,
                               'address': profile.address})  # ad_line1': profile.ad_line1, 'ad_line2': profile.ad_line2, 'ad_city': profile.ad_city, 'ad_postcode': profile.ad_postcode, 'ad_country': profile.ad_country})
    form.fields['dob'].widget = DatePickerInput()
    form.fields['address'].widget = GooglePointFieldWidget()
    ecformset = ECSet(instance=request.user.patient)

    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=request.user.patient)
        ecformset = ECSet(request.POST or None,
                          request.FILES or None, instance=request.user.patient)

        if form.is_valid() and ecformset.is_valid():
            # form.save()
            profile = form.save(commit=False)
            profile.save()

            ecformset.save()

            return redirect('patient_home', id)

        else:
            form = PatientProfileForm(instance=request.user.patient)
            ecformset = ECSet(request.GET or None,
                              instance=request.user.patient)
            print(form.errors)

    context = {
        'form': form,
        'ecformset': ecformset,
        'profile': profile,
    }

    response = render(
        request, 'myhealthdb/patient/patient_details_update.html', context)
    return response


@user_passes_test(staff_check, redirect_field_name='home_base')
def task_home(request, id):

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    now = timezone.now()

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]

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

    context = {
        'profile': profile,
        'my_tasks_overdue': my_tasks_overdue,
        'my_tasks_due': my_tasks_due,
        'my_tasks_finished': my_tasks_finished,
        'tasks_by_me_overdue': tasks_by_me_overdue,
        'tasks_by_me_due': tasks_by_me_due,
        'tasks_by_me_finished': tasks_by_me_finished,
    }

    response = render(request, 'task/tasks.html', context)
    return response


@user_passes_test(staff_check, redirect_field_name='home_base')
def staff_details(request, id):

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]
    form = StaffProfileForm({'tel_no': profile.tel_no, 'first_name': profile.first_name,
                             'last_name': profile.last_name, 'ward': profile.ward})

    if request.method == 'POST':
        form = StaffProfileForm(request.POST, instance=request.user.doctor)

        if form.is_valid():
            # form.save()
            profile = form.save(commit=False)
            profile.save()
            return redirect('staff_home', id)
        else:
            form = StaffProfileForm(instance=request.user.staff)
            print(form.errors)

    context = {
        'form': form,
        'profile': profile,
    }

    response = render(request, 'myhealthdb/staff/staff_details.html', context)
    return response


@login_required(redirect_field_name='index')
def home_base(request):

    thisid = request.user.id
    if request.user.is_superuser:
        return redirect('admin:index')

    if request.user.user_type == 1:
        return redirect('patient_home', id=thisid)
    else:
        return redirect("staff_home", id=thisid)


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
