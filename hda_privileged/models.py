from time import gmtime, strftime

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User, AnonymousUser

# helper functions

def get_sentinel_user():
    """
    Returns a special user object to represent a user that is no longer in the system
    """
    return get_user_model().objects.get_or_create(username='deleted user').first()

def get_upload_path(instance, filename):
    nowgmt = gmtime()
    datestr = strftime("%Y-%m-%d", nowgmt)
    timestr = strftime("%H-%M-%S", nowgmt)
    return "uploads/{0}/{1}-{2}".format(datestr, timestr, filename)


# model classes

class Health_Indicator(models.Model):
    """
    Represents some health metric that we want to store data sets for, e.g. obesity, mortality, education, etc.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.name} ({self.id})"

    class Meta:
        verbose_name='Health indicator'


class Document(models.Model):
    """
    Represents a file that a privilged user uploads containing data to process
    """

    # where they got the data from
    source = models.CharField(max_length=144,
        blank=True,
        verbose_name="Data source",
        help_text="Describes where this data came from"
    )

    # when the file was uploaded (set automatically)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # user who uploaded the file (must be set in the view handling the upload)
    # is reset to a sentinel object if original user is deleted from the DB
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET(get_sentinel_user)
    )

    # the file
    file = models.FileField(upload_to=get_upload_path)


class Data_Set(models.Model):
    """
    A collection of data points for a single year and health indicator, generated from an uploaded document
    """

    # the health indicator/metric this data set is for
    indicator = models.ForeignKey(Health_Indicator,
        on_delete=models.CASCADE,
        related_name="data_sets"
    )
    # the year this data set covers
    # (not a date because we probably won't have an exact date)
    year = models.PositiveSmallIntegerField(validators=[
        MinValueValidator(1000, message="Years before 1000 C.E. are extremely unlikely..."),
        MaxValueValidator(9999, message="If it really is later than the year 9999, you should get someone to update this program"),
    ])

    source_document = models.ForeignKey(Document,
        on_delete=models.SET_NULL,
        null=True,
        related_name='data_sets'
    )

    def __str__(self):
        return f"Dataset {self.id} for indicator {self.indicator!s} and year {self.year:d}"

    class Meta:
        verbose_name='Data set'


class US_State(models.Model):
    """
    Represents a state in the U.S. (e.g. Wyoming, Virginia)
    We populate the DB with a known-good set of these; they should not be user-generated
    """
    short = models.CharField(primary_key=True, max_length=2)
    full = models.CharField(max_length=100)
    # Char instead of int because, like a phone number, we don't want to truncate leading zeros!
    fips = models.CharField(max_length=2)

    def __str__(self):
        return self.fips + ' - ' + self.short + ' - ' + self.full

    class Meta:
        verbose_name='US state'


class US_County(models.Model):
    """
    Represents a county or county-equivalent in a State in the U.S.
    We populate the DB with a known-good set of these; they should not be user-generated
    """
    fips = models.CharField(max_length=3)
    name = models.CharField(max_length=200)
    state = models.ForeignKey(US_State, related_name='counties', on_delete=models.CASCADE)

    def __str__(self):
        return self.fips + ' - '+ self.name +' - '+ self.state_id

    class Meta:
        verbose_name='US county'
        verbose_name_plural='US counties'


class Data_Point(models.Model):
    """
    A single measurement for a particulr county and data set
    """
    value = models.FloatField(default=0,
        help_text="The measured value for this county for this data set"
    )

    percentile = models.FloatField(default=0,
        help_text="The percentile for this value, calculated against the other data points in the data set",
        validators=[
            MinValueValidator(0, message="Percentiles cannot be less than 0")
        ]
    )

    county = models.ForeignKey(US_County, models.CASCADE, related_name='data_points')

    data_set = models.ForeignKey(Data_Set, models.CASCADE, related_name='data_points')

    class Meta:
        verbose_name='Data point'
