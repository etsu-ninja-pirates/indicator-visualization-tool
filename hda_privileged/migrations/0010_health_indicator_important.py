# Generated by Django 2.1.5 on 2019-02-21 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hda_privileged', '0009_auto_20190129_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='health_indicator',
            name='important',
            field=models.BooleanField(default=False, help_text='Display a chart for this indicator on the overview page for a state or county', verbose_name='Show on overview'),
        ),
    ]