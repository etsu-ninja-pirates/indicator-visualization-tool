from django.contrib.auth import authenticate, login
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.template import Context
from django.template.loader import get_template

from hda_privileged.forms import LoginForm

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
