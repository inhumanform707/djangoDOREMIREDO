# Generated by Django 5.1.6 on 2025-02-19 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doremiredo', '0006_student_is_active_alter_payment_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='note',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='note',
            field=models.TextField(blank=True),
        ),
    ]
