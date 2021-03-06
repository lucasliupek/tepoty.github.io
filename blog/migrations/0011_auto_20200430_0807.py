# Generated by Django 2.1.2 on 2020-04-30 08:07

from django.db import migrations, models
import django.db.models.deletion
import embed_video.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_auto_20200430_0757'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='video',
            field=embed_video.fields.EmbedVideoField(blank=True),
        ),
        migrations.AlterField(
            model_name='comment',
            name='post_connected',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Post'),
        ),
    ]
