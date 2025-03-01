import os
import django
from django.db import connection
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_django_project.settings')
django.setup()

def test_connection():
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            print("Database connection successful!")
            print(f"Connected to: {settings.DATABASES['default']['HOST']}")
            return True
    except Exception as e:
        print(f"Database connection failed: {str(e)}")
        return False

if __name__ == '__main__':
    test_connection()
