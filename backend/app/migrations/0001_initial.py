# Generated by Django 5.1.5 on 2025-02-12 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('multiuser_mode', models.BooleanField(blank=True, default=False, help_text='Whether app is used by more than one user. Provides form to add new user, if True.')),
                ('passwordless_login', models.BooleanField(blank=True, default=False, help_text='Whether app requires a password to log on. If running locally on a computer with trusted users, then set this to True. Set False if running as a web server or local privacy is desired.')),
                ('show_users_on_login_screen', models.BooleanField(blank=True, default=False, help_text='Show or hide the available users. If running in single-user mode with passwordless login, set this to True. If running on the web or with untrusted users, set this to False.')),
            ],
            options={
                'verbose_name_plural': 'App Settings',
                'ordering': ['created'],
            },
        ),
    ]
