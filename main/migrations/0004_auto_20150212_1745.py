# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20150211_1949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='imgfile',
            field=models.ImageField(upload_to=b'%Y_%m_%d'),
            preserve_default=True,
        ),
    ]
