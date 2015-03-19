# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20150211_1946'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image',
            old_name='docfile',
            new_name='imgfile',
        ),
    ]
