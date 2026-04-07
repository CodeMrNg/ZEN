import calendar

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_tradingpreference_default_dashboard_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='tradingpreference',
            name='default_week_start_day',
            field=models.PositiveSmallIntegerField(
                choices=[
                    (0, 'Monday'),
                    (1, 'Tuesday'),
                    (2, 'Wednesday'),
                    (3, 'Thursday'),
                    (4, 'Friday'),
                    (5, 'Saturday'),
                    (6, 'Sunday'),
                ],
                default=calendar.SUNDAY,
            ),
        ),
    ]
