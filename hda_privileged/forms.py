from django import forms
from .models import Document, Health_Indicator


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':"form-control", 'placeholder': "Username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':"form-control", 'placeholder': "Password"}))


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = ('source', 'file',)


# Not using a ModelForm because this needs to include data for
# both Document and Data_Set model classes - we could make an
# additional Model class (e.g. NewDataUpload entity) with the
# right fields and then create a ModelForm from that, but that
# seems like an extra step.
class UploadNewDataForm(forms.Form):
    """
    Form subclass for displaying an upload form for new data sets.
    """
    file = forms.FileField(
        label='Data File',
        help_text='File containing data in CSV format'
    )

    ## TODO ##
    ## This needs to be required once we have a way to create new ones ##
    indicator = forms.ModelChoiceField(
        queryset=Health_Indicator.objects.all(),
        label='Health indicator',
        help_text='The health indicator/metric that this file contains data for',
        required=False
    )

    source = forms.CharField(
        label='Data source',
        help_text='The source/provenance of the data',
        required=False,
        widget=forms.Textarea
    )

    year = forms.IntegerField(
        label='Data year',
        help_text='Year this data is from',
        min_value=1000,
        max_value=9999
    )

