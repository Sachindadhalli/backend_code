# Generated by Django 2.2.1 on 2019-05-24 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_seeker', '0002_seekerprofile_resume_headline'),
    ]

    operations = [
        migrations.AddField(
            model_name='seekerprofile',
            name='photo_path',
            field=models.FileField(blank=True, null=True, upload_to='photo/%Y/%m/%D/'),
        ),
    ]
