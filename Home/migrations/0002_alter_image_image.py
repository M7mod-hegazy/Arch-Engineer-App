# Generated by Django 4.2.7 on 2025-02-27 11:59

import Home.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(blank=True, null=True, storage=Home.storage.SupabaseStorage(), upload_to='images'),
        ),
    ]
