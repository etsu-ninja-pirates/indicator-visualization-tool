from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView


from .forms import LoginForm, UploadNewDataForm
from .models import Document, Data_Set, Data_Point, Percentile
from .percentile import get_percentiles_for_points, assign_percentiles_to_points
from .upload_reading import read_data_points_from_file


# ------------------------------------------------
# The user_log-in function will handle the log in
# functionality and redirect the loggedin user to
# desired page
# ------------------------------------------------
def user_login(request):
    form = LoginForm()
    next = ""
    if request.GET:
        next = request.GET['next']
    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # The 'sample' routing will be changed to the desired landing page
                    # that will be displayed after authenticated user logs in
                    # If there is no next page to rout to, the routing will go to the
                    # Default landing page
                    if next == "":
                        return redirect(reverse('priv:privdashboard'))
                    else:
                        # If there is a next page, the routing will automatical go to the
                        # next page after a user is authenticated
                        return redirect(next)
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    args = {'form': form, 'next': next}
    return render(request, 'hda_privileged/login.html', args)


def logout_view(request):
    logout(request)
    return redirect('priv:login')


def create_metric(request):
    return render(request, 'hda_privileged/create_metric.html')


def manage_metrics(request):
    return render(request, 'hda_privileged/manage_metrics.html')


def sampleNavBar(request):
    return render(request, 'hda_privileged/sample.html')


class PrivDashboardView(TemplateView):
    template_name = 'hda_privileged/privdashboard.html'

    def get_context_data(self, **kwargs):
        #get indicators for left side of view
        datasets = Data_Set.objects.all()
        ds = []       
        for i in datasets:
            if i.indicator.name not in ds:
                ds.append(i) 
                

        #call super to get the base context
        context = super().get_context_data(**kwargs)

        # did the URL specify an indicator? Get indicator and save in context
        selected_indicator = self.kwargs.get('indicator', None) 
        context['selected_indicator'] = selected_indicator 
               

        #retrieve all dataset objects for searching
        temp_data = Data_Set.objects.all()  
        fls = []      

        #if user has selected an indicator
        if selected_indicator is not None:
            for td in temp_data:
                #if the data set indicator matches the user indicator
                if(td.indicator.name == selected_indicator):
                    fls.append(td)     
            #Create message for user
            context['indicator_message'] = "Data Files for " + selected_indicator              

        #user has not selected an indicator, display all files
        elif selected_indicator is None:           
            for td in temp_data:
                fls.append(td)
            #Create message for user
            context['indicator_message'] = "Data File List for all Indicators"

        #error retrieving files for indicator, display all files
        else:
            for td in temp_data:
                fls.append(td)
            #Create message for user
            context['indicator_message'] = "Indicator not found: Returning all files"

        #put indicators and files in context
        context['files'] = fls
        context ['datasets'] = ds
        return context    

    
 
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

        # Create and save a Data Set here! ##
        indicator = form.cleaned_data['indicator']
        year = form.cleaned_data['year']

        data_set = Data_Set(
            indicator=indicator,
            year=year,
            source_document=doc
        )

        data_set.save()

        format_choice = form.cleaned_data['column_format']
        doc.file.open(mode='rt')
        data_points = read_data_points_from_file(doc.file, format_choice, data_set)
        doc.file.close()

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
