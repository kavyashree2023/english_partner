# Generated by Django 4.2.5 on 2024-01-07 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('counsellorApp', '0003_counsellorinfo_amount_spent'),
    ]

    operations = [
        migrations.AddField(
            model_name='admininfo',
            name='socialMedia',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='counsellorinfo',
            name='socialMedia',
            field=models.IntegerField(null=True),
        ),
    ]
