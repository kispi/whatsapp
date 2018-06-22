# Generated by Django 2.0.5 on 2018-05-29 08:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('whatsapp', '0004_log_broadcasted'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='contact',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='whatsapp.Contact'),
        ),
        migrations.AlterField(
            model_name='log',
            name='message',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='whatsapp.Message'),
        ),
    ]
