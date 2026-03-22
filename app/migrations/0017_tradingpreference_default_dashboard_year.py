import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_alter_trade_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='tradingpreference',
            name='default_dashboard_year',
            field=models.PositiveSmallIntegerField(default=app.models.current_local_year),
        ),
    ]
