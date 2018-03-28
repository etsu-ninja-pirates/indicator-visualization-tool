from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render

from hda_auth.form import LoginForm

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
    return render(request, 'hda_auth/login.html',args)
