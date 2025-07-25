#!/usr/bin/env python
import os
import sys
import django
import json
from io import StringIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'perswebsite.settings')
django.setup()

from django.core.management import call_command
from django.apps import apps


def export_clean_data():
    """Export all myapp data to clean JSON file"""

    # Get all models from myapp
    app_config = apps.get_app_config('myapp')
    models = app_config.get_models()

    print("Found models:")
    for model in models:
        count = model.objects.count()
        print(f"  - {model._meta.label}: {count} records")

    # Export data using Django's serializer
    output = StringIO()

    try:
        # Export all myapp models
        call_command(
            'dumpdata',
            'myapp',
            format='json',
            indent=2,
            stdout=output,
            use_natural_foreign_keys=True,
            use_natural_primary_keys=False
        )

        # Get the JSON string
        json_data = output.getvalue()

        # Clean up any problematic characters
        json_data = json_data.encode('ascii', 'ignore').decode('ascii')

        # Validate JSON
        try:
            json.loads(json_data)
            print("✓ JSON is valid")
        except json.JSONDecodeError as e:
            print(f"✗ JSON validation failed: {e}")
            return False

        # Write to file with UTF-8 encoding
        with open('working_data.json', 'w', encoding='utf-8') as f:
            f.write(json_data)

        print("✓ Data exported to working_data.json")
        return True

    except Exception as e:
        print(f"✗ Export failed: {e}")
        return False

    finally:
        output.close()


if __name__ == "__main__":
    export_clean_data()