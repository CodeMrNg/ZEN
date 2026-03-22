from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_tradescreenshot'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='result',
            field=models.CharField(
                blank=True,
                choices=[
                    ('TAKE_PROFIT', 'Take profit'),
                    ('GAIN', 'Gain'),
                    ('BREAK_EVEN', 'Break even'),
                    ('STOP_LOSS', 'Stoploss'),
                    ('LOSS', 'Perte'),
                ],
                max_length=12,
            ),
        ),
    ]
