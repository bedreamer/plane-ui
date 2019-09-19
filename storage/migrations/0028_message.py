# Generated by Django 2.2.4 on 2019-09-08 05:22

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0027_flowfilehistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(default='info', help_text='消息类型，info/warn/error', max_length=100)),
                ('create_datetime', models.DateTimeField(default=django.utils.timezone.now, help_text='消息更新时间')),
                ('expire_datetime', models.DateTimeField(default='2099-12-31 23:59:59.999', help_text='过期时间')),
                ('title', models.CharField(default='消息', help_text='消息标题', max_length=100)),
                ('txt', models.TextField(default='', help_text='消息主体内容')),
                ('ref_href', models.TextField(default='', help_text='参考链接')),
                ('ref_title', models.CharField(default='参考', help_text='参考链接标题', max_length=100)),
                ('ref_target', models.CharField(default='_self', help_text='参考链接打开方式， _blank, _self', max_length=100)),
            ],
        ),
    ]
