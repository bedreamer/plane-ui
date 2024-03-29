# Generated by Django 2.2.4 on 2019-09-02 07:50

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0021_auto_20190831_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flowfile',
            name='create_datetime',
            field=models.DateTimeField(default=datetime.datetime(2019, 9, 2, 7, 50, 12, 892830, tzinfo=utc), help_text='流程创建时间'),
        ),
        migrations.AlterField(
            model_name='flowfile',
            name='update_datetime',
            field=models.DateTimeField(default=datetime.datetime(2019, 9, 2, 7, 50, 12, 892855, tzinfo=utc), help_text='流程更新时间'),
        ),
        migrations.AlterField(
            model_name='planedefaultdevice',
            name='update_datetime',
            field=models.DateTimeField(default=datetime.datetime(2019, 9, 2, 7, 50, 12, 890376, tzinfo=utc), help_text='设置为默认设备的日期时间'),
        ),
        migrations.AlterField(
            model_name='planedevice',
            name='create_datetime',
            field=models.DateTimeField(default=datetime.datetime(2019, 9, 2, 7, 50, 12, 889687, tzinfo=utc), help_text='设备驱动创建时间'),
        ),
        migrations.AlterField(
            model_name='planedevicehistory',
            name='operation_datetime',
            field=models.DateTimeField(default=datetime.datetime(2019, 9, 2, 7, 50, 12, 890857, tzinfo=utc), help_text='操作时间'),
        ),
        migrations.AlterField(
            model_name='project',
            name='create_datetime',
            field=models.DateTimeField(default=datetime.datetime(2019, 9, 2, 7, 50, 12, 891321, tzinfo=utc), help_text='项目创建时间'),
        ),
        migrations.AlterField(
            model_name='projectstatelog',
            name='change_datetime',
            field=models.DateTimeField(default=datetime.datetime(2019, 9, 2, 7, 50, 12, 891804, tzinfo=utc), help_text='切换时间'),
        ),
        migrations.AlterField(
            model_name='projectwithflow',
            name='bind_datetime',
            field=models.DateTimeField(default=datetime.datetime(2019, 9, 2, 7, 50, 12, 893310, tzinfo=utc), help_text='绑定时间'),
        ),
    ]
