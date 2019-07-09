from django.http import HttpResponse
from django.shortcuts import render, redirect
from registration.backends.simple.views import RegistrationView


# Create your views here.
def index(request):

    context_dict = {}
    response = render(request, 'myhealthdb/index.html', context_dict)

    return response