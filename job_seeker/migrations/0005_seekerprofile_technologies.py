# Generated by Django 2.2.1 on 2019-05-27 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_seeker', '0004_seekerprofile_skill_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='seekerprofile',
            name='technologies',
            field=models.CharField(max_length=40, null=True),
        ),
    ]
