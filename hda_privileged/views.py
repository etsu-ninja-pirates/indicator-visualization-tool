from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect

from django.template import Context
from django.template.loader import get_template
from django.core.files.storage import FileSystemStorage


from hda_privileged.forms import LoginForm, DocumentForm
from .models import Document

#------------------------------------------------
#The user_log-in function will handle the log in
# functionality and redirect the loggedin user to
# desired page
#------------------------------------------------


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request,user)
                    return HttpResponse('You Successfully Logged in')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
        args = {'form': form}
    return render(request, 'hda_privileged/login.html', args)


def create_metric(request):
    return render(request, 'hda_privileged/create_metric.html')


def manage_metrics(request):
    return render(request, 'hda_privileged/manage_metrics.html')


def sampleNavBar(request):
    return render(request, 'hda_privileged/sample.html')


#def upload_metric(request):
 #   return render(request, 'hda_privileged/upload_metric.html')


def upload_metric(request):

    if request.method == 'POST' and request.FILES['myfile']:
        form = DocumentForm(request.POST, request.FILES)
        myfile = request.FILES['myfile']

        if myfile.name.lower().endswith(('.csv')):
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            fs.url(filename)
            if filename:
                messages.success(request, 'File Successfully Uploaded.')
            else:
                messages.success(request, "Error in File Upload, Try Again.")
        else:
            messages.success(request, "Error in File Upload, File not CSV.")
                    
        return render(request,'hda_privileged/upload_metric.html')
        #return render(request, 'core/simple_upload.html', { 3 line from here down commented before
        #   'uploaded_file_url': uploaded_file_url
        #})
    else:
        form = DocumentForm()
        #messages.success(request, "Error in File Upload, Try Again")
        return render(request, 'hda_privileged/upload_metric.html', {'form': form})
    #return render(request, 'core/simple_upload.html')



