from dotenv import load_dotenv
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "whatsapp.settings")
    try:
        from django.core.management import execute_from_command_line
        import django
        django.setup()

        # Override default port for `runserver` command
        from django.core.management.commands.runserver import Command as runserver
        runserver.default_port = os.getenv('API_PORT')
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)