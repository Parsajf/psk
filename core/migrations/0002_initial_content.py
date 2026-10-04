import json
from pathlib import Path
from django.db import migrations


def seed(apps, schema_editor):
    fixture = Path(__file__).resolve().parent.parent / 'fixtures' / 'initial_content.json'
    data = json.loads(fixture.read_text())
    for item in data:
        model_name = item['model'].split('.')[1]
        model = apps.get_model('core', model_name)
        model.objects.using(schema_editor.connection.alias).get_or_create(
            pk=item['pk'], defaults=item['fields']
        )


class Migration(migrations.Migration):
    dependencies = [('core', '0001_initial')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
