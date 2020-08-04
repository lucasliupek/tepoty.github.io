# Generated by Django 2.1.2 on 2020-05-03 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20200502_1005'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='user_role',
        ),
        migrations.AddField(
            model_name='profile',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_contentcreator',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='UserRole',
        ),
    ]
