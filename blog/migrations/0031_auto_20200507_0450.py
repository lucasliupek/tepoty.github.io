# Generated by Django 2.1.2 on 2020-05-07 04:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0030_auto_20200507_0440'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='post_connected',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Post'),
        ),
        migrations.AlterField(
            model_name='contentitem',
            name='item_price',
            field=models.BigIntegerField(default=0),
        ),
    ]
