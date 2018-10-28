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
from django.views.generic import TemplateView
import csv
from csv import DictReader
from django.core.management import BaseCommand
from django.shortcuts import render

from .forms import LoginForm, DocumentForm, UploadNewDataForm
from .models import Document,US_County, Health_Indicator, Data_Set, Data_Point, Percentile
from .percentile import get_percentiles_for_points, assign_percentiles_to_points

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


class PrivDashboardView(TemplateView):
    template_name = 'hda_privileged/privdashboard.html'

    def get_view(self, request):
        return render(request,self.template_name)
 
 
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
        saved_document = doc.save()
        messages.success(request, "Document uploaded successfully")


        ## Create and save a Data Set here! ##
        indicator = form.cleaned_data['indicator']
        year = form.cleaned_data['year']
        data_source = form.cleaned_data['source']

        data_set = Data_Set(
            indicator=indicator,
            year=year,
            source_document=doc
        )

        data_set.save()

        data_points = []

        # reading the value from the selected file
        f = open('.' + data_set.source_document.file.url, 'r')
        for row in csv.DictReader(f):
            # get county and state from csv row
            county = row['NAME']
            state = row['STATE_USPS']

            # get associated county
            associated_county = US_County.objects.get(name=county, state=state)

            # build Data_Point instance
            data_point = Data_Point(
                value=int(row['Value']),
                county=associated_county,
                data_set=data_set
            )
            data_points.append(data_point)

        # we are done reading from the file
        f.close()

        # calculate the percentile-values for this data set
        percentile_values = get_percentiles_for_points(data_points)

        # assign a percentile to each data point
        assign_percentiles_to_points(data_points, percentile_values)

        # transform our list of tuples List<(P, PV)> into a list of Percentile model objects
        percentile_models = [Percentile(rank=p, value=pv, data_set=data_set) for (p, pv) in percentile_values]


        # save all the data points and percentile values using bulk_create, for speed
        Data_Point.objects.bulk_create(data_points)
        Percentile.objects.bulk_create(percentile_models)

        # This is mostly for debugging, but it's a useful example of using the messages API
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
