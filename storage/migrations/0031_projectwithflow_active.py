# Generated by Django 2.2.4 on 2019-09-11 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0030_auto_20190908_0657'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectwithflow',
            name='active',
            field=models.BooleanField(default=False, help_text='流程是否处于激活/执行状态'),
        ),
    ]
