from django import forms
from django.forms import ModelForm

from .models import Health_Indicator
from .upload_reading import UPLOAD_FORMAT_CHOICES, CHOICE_NAME


class HealthIndicatorForm(ModelForm):
    """
    health indicator form (for multichart view)
    """
    class Meta:
        """ """
        model = Health_Indicator
        fields = ['name', 'important']
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g. \'Poor physical health days\'',
                    'size': 100,
                }
            )
        }


class LoginForm(forms.Form):
    """
    login form for user management

    """
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': "form-control", 'placeholder': "Username"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': "form-control", 'placeholder': "Password"}
        )
    )


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

    column_format = forms.ChoiceField(
        label='CSV file format',
        help_text='What columns to use to identify counties in the uploaded CSV file',
        widget=forms.RadioSelect,
        choices=UPLOAD_FORMAT_CHOICES,
        required=True,
        initial=CHOICE_NAME
    )

    # This needs to be required once we have a way to create new ones #
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
        widget=forms.Textarea(attrs={'rows': 3})
    )

    # The default value should not be hardcoded!
    year = forms.IntegerField(
        label='Data year',
        help_text='Year this data is from',
        initial=2018,
        min_value=1000,
        max_value=9999
    )

