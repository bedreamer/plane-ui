# Generated by Django 2.2.4 on 2019-09-07 05:29

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0026_auto_20190902_1631'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlowFileHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_datetime', models.DateTimeField(default=django.utils.timezone.now, help_text='流程更新时间')),
                ('flow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='storage.FlowFile')),
            ],
        ),
    ]