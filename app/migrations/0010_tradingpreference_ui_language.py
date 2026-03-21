from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_tradingaccount_archived_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='tradingpreference',
            name='ui_language',
            field=models.CharField(
                choices=[
                    ('fr', 'Francais'),
                    ('en', 'English'),
                    ('es', 'Espanol'),
                    ('pt', 'Portugues'),
                    ('ar', 'Arabic'),
                    ('zh-hans', 'Chinese'),
                ],
                default='fr',
                max_length=12,
            ),
        ),
    ]
