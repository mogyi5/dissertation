from django.http import HttpResponse
from django.shortcuts import render, redirect


# Create your views here.
def index(request):

    context_dict = {}
    response = render(request, 'myhealthdb/index.html', context_dict)

    return response

# def detail(request, question_id):
#     return HttpResponse("You're looking at question %s." % question_id)

# def results(request, question_id):
#     response = "You're looking at the results of question %s."
#     return HttpResponse(response % question_id)


