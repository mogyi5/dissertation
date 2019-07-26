from django.shortcuts import render, redirect, get_object_or_404
from allauth.account.views import SignupView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, user_passes_test
from myhealthdb.forms import PatientSignupForm, PatientProfileForm, StaffProfileForm, HospitalContactForm, ECSet, PDSet, EventBookingForm
from myhealthdb.models import CustomUser, Patient, Staff, PatientEm, Event, PatientDoctor, Group
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic import DetailView
from django.urls import reverse_lazy
from django.db import transaction, IntegrityError
from django.contrib import messages
from time import sleep
from django.utils import timezone
from datetime import date
from django.contrib.postgres.search import SearchVector
# from haystack.generic_views import SearchView



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

# class AdvancedSearchView(SearchView):
#     form_class = PatientSearchForm
#     template_name = 'search/advanced_search.html'
#     """My custom search view."""

#     def get_queryset(self):
#         queryset = super(AdvancedSearchView, self).get_queryset()
#         # further filter queryset based on some set of criteria
#         return queryset#   .filter(pub_date__gte=date(2015, 1, 1))

#     def get_context_data(self, *args, **kwargs):
#         context = super(AdvancedSearchView, self).get_context_data(*args, **kwargs)
#         profile = Staff.objects.get_or_create(
#             baseuser=self.request.user)[0]
#         context['profile'] = profile
#         return context


# def advanced_search(request, id):

#     if id != request.user.id:
#         return redirect('home_base')

#     try:
#         baseuser = CustomUser.objects.get(id=id)
#     except CustomUser.DoesNotExist:
#         return redirect('index')

#     profile = Staff.objects.get_or_create(baseuser=baseuser)[0]

#     context = {
#         'profile': profile,
#     }

#     context_dict = {}
#     response = render(request, 'search/advanced_search.html', context)

#     return response

#@user_passes_test(staff_check, redirect_field_name='home_base')
class GroupDetailsView(DetailView):
    model = Group
    template_name = 'myhealthdb/staff/groups.html'

    def get_context_data(self, **kwargs):
        context = super(GroupDetailsView, self).get_context_data(**kwargs)
        profile = Staff.objects.get_or_create(baseuser=self.request.user)[0]
        context['profile'] = profile
        return context

    # def get(self, request, *args, **kwargs):
    #     group = get_object_or_404(Group, slug=kwargs['slug'])
    #     context = {'group': group}
    #     return render(request, 'myhealthdb/staff/groups.html', context)


#@user_passes_test(staff_check, redirect_field_name='home_base') ##add these ok
class PatientSearchResultsView(ListView):
    model = Patient
    template_name = 'search/patient_search_results.html'

    def get_context_data(self, **kwargs):
        context = super(PatientSearchResultsView,
                        self).get_context_data(**kwargs)
        profile = Staff.objects.get_or_create(
            baseuser=self.request.user)[0]
        context['profile'] = profile
        return context

    def get_queryset(self):  # new
        query = self.request.GET.get('q', '')

        vector = SearchVector('first_name', 'last_name')

        my_patients = Patient.objects.all() # have this not all()
        object_list = my_patients.annotate(search = vector).filter(search=query)

        #Patient.objects.filter(SearchVector('first_name', 'last_name') = query)
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
    fields = ('letter', 'date_in', 'date_out', 'pd_relation', 'notes', 'done')
    template_name = 'event/event_update_form.html'
    pk_url_kwarg = 'event_pk'
    #context_object_name = 'event'

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
        #event.updated_by = self.request.profile
        event.save()
        return redirect('home_base')  # event_pk=event.id)


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
    try:
        pdrelations = PatientDoctor.objects.get(patient=profile)
        events = pdrelations.reversepd.filter(date_in__gte=timezone.now())

        context = {
            'events': events,
            'profile': profile,
        }
    except PatientDoctor.DoesNotExist:
        context = {
            'profile': profile,
        }

    response = render(request, 'myhealthdb/patient/patient_home.html', context)

    return response


@user_passes_test(staff_check, redirect_field_name='home_base')
def staff_home(request, id):

    context = {
    }

    if id != request.user.id:
        return redirect('home_base')

    try:
        baseuser = CustomUser.objects.get(id=id)
    except CustomUser.DoesNotExist:
        return redirect('index')

    profile = Staff.objects.get_or_create(baseuser=baseuser)[0]
    context['profile']=profile

    try:       
        groups = Group.objects.filter(members=profile)
        context['groups']=groups
    except Group.DoesNotExist:
        pass

    # try:                                                                         ##this needs fixed too
    #     pdrelations = PatientDoctor.objects.filter(doctor=profile)
    #     events = pdrelations.reversepd.filter(date_in__date=date.today())
    #     try:
    #         inpatients = PatientDoctor.objects.filter(inpatient=True)

    #         context = {
    #             'events': events,
    #             'profile': profile,
    #             'inpatients': inpatients
    #         }

    #     except PatientDoctor.DoesNotExist:
    #         context = {
    #             'events': events,
    #             'profile': profile,
    #         }

    # except PatientDoctor.DoesNotExist:
    # context = {
    #     'profile': profile,
    # }

    response = render(request, 'myhealthdb/staff/staff_home.html', context)

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
    form = PatientProfileForm({'dob': profile.dob, 'first_name': profile.first_name, 'last_name': profile.last_name, 'sex': profile.sex, 'tel_no': profile.tel_no, 'nhs_no': profile.nhs_no,
                               'ad_line1': profile.ad_line1, 'ad_line2': profile.ad_line2, 'ad_city': profile.ad_city, 'ad_postcode': profile.ad_postcode, 'ad_country': profile.ad_country})

    ecformset = ECSet(instance=request.user.patient)
    pdformset = PDSet(instance=request.user.patient)

    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=request.user.patient)
        ecformset = ECSet(request.POST or None,
                          request.FILES or None, instance=request.user.patient)
        pdformset = PDSet(request.POST or None,
                          request.FILES or None, instance=request.user.patient)

        if form.is_valid() and ecformset.is_valid() and pdformset.is_valid():
            # form.save()
            profile = form.save(commit=False)
            profile.save()

            ecformset.save()
            pdformset.save()

            return redirect('patient_home', id)

        else:
            form = PatientProfileForm(instance=request.user.patient)
            ecformset = ECSet(request.GET or None,
                              instance=request.user.patient)
            pdformset = PDSet(request.GET or None,
                              instance=request.user.patient)
            print(form.errors)

    context = {
        'form': form,
        'ecformset': ecformset,
        'pdformset': pdformset,
        'profile': profile,
    }

    response = render(
        request, 'myhealthdb/patient/patient_details.html', context)
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
        form = StaffProfileForm(request.POST, instance=request.user.staff)

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
