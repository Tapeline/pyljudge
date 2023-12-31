# Generated by Django 4.1.4 on 2023-11-30 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_tasksubmit_verdict'),
    ]

    operations = [
        migrations.AddField(
            model_name='autotest',
            name='time_limit',
            field=models.IntegerField(default=5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='task',
            name='test_ordering',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tasksubmit',
            name='compiler',
            field=models.CharField(default='python', max_length=255),
            preserve_default=False,
        ),
    ]
