# Generated by Django 2.2.1 on 2019-05-25 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_seeker', '0003_seekerprofile_photo_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='seekerprofile',
            name='skill_name',
            field=models.CharField(max_length=300, null=True),
        ),
    ]
