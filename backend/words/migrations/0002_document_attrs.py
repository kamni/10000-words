# Generated by Django 5.1.5 on 2025-02-27 08:38

import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('words', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='attrs',
            field=models.JSONField(blank=True, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True),
        ),
    ]
