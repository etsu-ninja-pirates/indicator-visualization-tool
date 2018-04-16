from django.shortcuts import render

from django.http import HttpResponse


# Create your views here.
def create(request):
    return render(request, 'hda_createHMetrix/createMI.html')
