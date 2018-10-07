import os.path

from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import Context
from django.template.loader import get_template
from django.urls import reverse
from django.views import View

from .forms import LoginForm, DocumentForm, UploadNewDataForm
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

class UploadNewDataView(View):

    form_class = UploadNewDataForm
    template_name = 'hda_privileged/upload_metric.html'
    file_field_name = 'file'


    def _get_uploaded_file(self, request):
        return request.FILES[self.file_field_name]


    def _check_file_ext(self, request):
        uploaded_file = self._get_uploaded_file(request)

        okay = uploaded_file is not None and \
            uploaded_file.name.lower().endswith(('.csv'))

        if not okay:
            messages.warning(request, "Error in file upload, file was not CSV")

        return okay


    def _handle_form_submission(self, request, form):
        myfile = self._get_uploaded_file(request)

        # create a Document class instance
        doc = Document(
            file=myfile,
            source=form.cleaned_data['source']
        )

        # add a user if we have one
        if request.user.is_authenticated:
            doc.user = get_user(request)

        # this saves the file in the directory specified
        # in the Document model FileField.upload_to attribute
        # and saves the rest of the model in the database
        doc.save()
        messages.success(request, "Document uploaded successfully")

        ## TODO ##
        ## Create and save a Data Set here! ##
        indicator = form.cleaned_data['indicator']
        messages.info(request, f"Indicator was {indicator!s}")


    def get(self, request, *args, **kwargs):
        # unbound form
        form = self.form_class()
        return render(request, self.template_name, {'form': form})


    def post(self, request, *args, **kwargs):
        # bind the form
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid() and self._check_file_ext(request):
            # Is there a Django-y way of adding more validation?
            self._handle_form_submission(request, form)

        return render(request, self.template_name, {'form': form})
