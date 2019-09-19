# Generated by Django 2.2.4 on 2019-08-31 09:00

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0020_auto_20190831_1624'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flowfile',
            name='origin_name',
        ),
        migrations.AddField(
            model_name='flowfile',
            name='origin_path',
            field=models.TextField(default='', help_text='原始流程文件路径'),
        ),
        migrations.AddField(
            model_name='projectwithflow',
            name='bind_datetime',
            field=models.DateTimeField(default=datetime.datetime(2019, 8, 31, 9, 0, 47, 437149, tzinfo=utc), help_text='绑定时间'),
        ),
        migrations.AddField(
            model_name='projectwithflow',
            name='comment',
            field=models.TextField(default='', help_text='对这个流程的备注说明'),
        ),
        migrations.AlterField(
            model_name='flowfile',
            name='create_datetime',
            field=models.DateTimeField(default=datetime.datetime(2019, 8, 31, 9, 0, 47, 436580, tzinfo=utc), help_text='流程创建时间'),
        ),
        migrations.AlterField(
            model_name='flowfile',
            name='update_datetime',
            field=models.DateTimeField(default=datetime.datetime(2019, 8, 31, 9, 0, 47, 436609, tzinfo=utc), help_text='流程更新时间'),
        ),
        migrations.AlterField(
            model_name='planedefaultdevice',
            name='update_datetime',
            field=models.DateTimeField(default=datetime.datetime(2019, 8, 31, 9, 0, 47, 429055, tzinfo=utc), help_text='设置为默认设备的日期时间'),
        ),
        migrations.AlterField(
            model_name='planedevice',
            name='create_datetime',
            field=models.DateTimeField(default=datetime.datetime(2019, 8, 31, 9, 0, 47, 428103, tzinfo=utc), help_text='设备驱动创建时间'),
        ),
        migrations.AlterField(
            model_name='planedevicehistory',
            name='operation_datetime',
            field=models.DateTimeField(default=datetime.datetime(2019, 8, 31, 9, 0, 47, 430151, tzinfo=utc), help_text='操作时间'),
        ),
        migrations.AlterField(
            model_name='project',
            name='create_datetime',
            field=models.DateTimeField(default=datetime.datetime(2019, 8, 31, 9, 0, 47, 433840, tzinfo=utc), help_text='项目创建时间'),
        ),
        migrations.AlterField(
            model_name='projectstatelog',
            name='change_datetime',
            field=models.DateTimeField(default=datetime.datetime(2019, 8, 31, 9, 0, 47, 435051, tzinfo=utc), help_text='切换时间'),
        ),
    ]
