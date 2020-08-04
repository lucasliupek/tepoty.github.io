# Generated by Django 2.1.2 on 2020-04-30 07:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_auto_20200430_0752'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='embedcontenttype_id',
        ),
        migrations.AddField(
            model_name='post',
            name='embedcontenttype',
            field=models.CharField(choices=[('YT', 'Youtube'), ('FB', 'Facebook'), ('IG', 'Instagram'), ('NONE', 'NONE')], default='NONE', max_length=4),
        ),
        migrations.AlterField(
            model_name='comment',
            name='post_connected',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blog.Post'),
        ),
        migrations.DeleteModel(
            name='EmbedContentType',
        ),
    ]
