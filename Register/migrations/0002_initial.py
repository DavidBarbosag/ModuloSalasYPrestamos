# Generated by Django 5.2 on 2025-04-30 20:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Register', '0001_initial'),
        ('Reservation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='register',
            name='reservationId',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='registers', to='Reservation.reservation'),
        ),
        migrations.AddIndex(
            model_name='register',
            index=models.Index(fields=['reservationId'], name='Register_re_reserva_d5f225_idx'),
        ),
    ]
