# Generated by Django 3.0.4 on 2020-07-15 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('camera_id', models.CharField(max_length=200)),
                ('time', models.CharField(max_length=200)),
                ('action', models.CharField(max_length=200)),
            ],
        ),
    ]
