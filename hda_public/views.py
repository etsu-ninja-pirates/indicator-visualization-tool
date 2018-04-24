from django.shortcuts import render

def dashboard(request):
    return render(request,'hda_public/dashboard.html', context= None)