# Generated by Django 2.0.3 on 2018-09-21 21:06

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import hda_privileged.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hda_privileged', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(blank=True, help_text='Describes where this data came from', max_length=144, verbose_name='Data source')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('file', models.FileField(upload_to=hda_privileged.models.get_upload_path)),
                ('user', models.ForeignKey(on_delete=models.SET(hda_privileged.models.get_sentinel_user), to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterModelOptions(
            name='data_point',
            options={'verbose_name': 'Data point'},
        ),
        migrations.AlterModelOptions(
            name='data_set',
            options={'verbose_name': 'Data set'},
        ),
        migrations.AlterModelOptions(
            name='health_indicator',
            options={'verbose_name': 'Health indicator'},
        ),
        migrations.AlterModelOptions(
            name='us_county',
            options={'verbose_name': 'US county', 'verbose_name_plural': 'US counties'},
        ),
        migrations.AlterModelOptions(
            name='us_state',
            options={'verbose_name': 'US state'},
        ),
        migrations.RemoveField(
            model_name='data_set',
            name='source',
        ),
        migrations.AlterField(
            model_name='data_point',
            name='county',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_points', to='hda_privileged.US_County'),
        ),
        migrations.AlterField(
            model_name='data_point',
            name='data_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_points', to='hda_privileged.Data_Set'),
        ),
        migrations.AlterField(
            model_name='data_point',
            name='percentile',
            field=models.FloatField(default=0, help_text='The percentile for this value, calculated against the other data points in the data set', validators=[django.core.validators.MinValueValidator(0, message='Percentiles cannot be less than 0')]),
        ),
        migrations.AlterField(
            model_name='data_point',
            name='value',
            field=models.FloatField(default=0, help_text='The measured value for this county for this data set'),
        ),
        migrations.AlterField(
            model_name='data_set',
            name='indicator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='data_sets', to='hda_privileged.Health_Indicator'),
        ),
        migrations.AlterField(
            model_name='data_set',
            name='year',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1000, message='Years before 1000 C.E. are extremely unlikely...'), django.core.validators.MaxValueValidator(9999, message='If it really is later than the year 9999, you should get someone to update this program')]),
        ),
        migrations.AlterField(
            model_name='health_indicator',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AddField(
            model_name='data_set',
            name='source_document',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data_sets', to='hda_privileged.Document'),
        ),
    ]
