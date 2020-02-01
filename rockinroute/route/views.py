from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'route/index.html')
    # return HttpResponse("Hello test")

def calculate(request):
    # print(request.POST.QueryDict)

    return HttpResponse("Hello test")

