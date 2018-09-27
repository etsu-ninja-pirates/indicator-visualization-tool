# Generated by Django 2.0.3 on 2018-09-17 02:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Data_Point',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.IntegerField(default=0)),
                ('percentile', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Data_Set',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.DateField()),
                ('source', models.CharField(max_length=200, verbose_name='')),
            ],
        ),
        migrations.CreateModel(
            name='Health_Indicator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='US_County',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fips', models.CharField(max_length=3)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='US_State',
            fields=[
                ('short', models.CharField(max_length=2, primary_key=True, serialize=False)),
                ('full', models.CharField(max_length=100)),
                ('fips', models.CharField(max_length=2)),
            ],
        ),
        migrations.AddField(
            model_name='us_county',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='counties', to='hda_privileged.US_State'),
        ),
        migrations.AddField(
            model_name='data_set',
            name='indicator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hda_privileged.Health_Indicator'),
        ),
        migrations.AddField(
            model_name='data_point',
            name='county',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hda_privileged.US_County'),
        ),
        migrations.AddField(
            model_name='data_point',
            name='data_set',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hda_privileged.Data_Set'),
        ),
    ]
