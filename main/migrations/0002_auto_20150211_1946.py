# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='docfile',
            field=models.FileField(upload_to=b'chartimage/%Y_%m_%d'),
            preserve_default=True,
        ),
    ]
