# Generated by Django 3.0.4 on 2020-07-15 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='logs',
            name='latitude',
            field=models.FloatField(default=19),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='logs',
            name='longitude',
            field=models.FloatField(default=72),
            preserve_default=False,
        ),
    ]
