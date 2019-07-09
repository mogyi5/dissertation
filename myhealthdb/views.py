from django.http import HttpResponse
from django.shortcuts import render, redirect


# Create your views here.
def index(request):

    context_dict = {}
    response = render(request, 'myhealthdb/index.html', context_dict)

    return response
    


