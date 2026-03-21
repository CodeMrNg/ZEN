from django.db import migrations


def normalize_ui_language(apps, schema_editor):
    TradingPreference = apps.get_model("app", "TradingPreference")
    TradingPreference.objects.exclude(ui_language__in=["fr", "en"]).update(ui_language="fr")


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0012_serverrefreshstatus"),
    ]

    operations = [
        migrations.RunPython(normalize_ui_language, migrations.RunPython.noop),
    ]
