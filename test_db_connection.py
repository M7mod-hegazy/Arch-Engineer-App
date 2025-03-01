import os
import django
from django.db import connection
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_django_project.settings')
django.setup()

def test_db():
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT version();')
            version = cursor.fetchone()
            print("Successfully connected to database!")
            print(f"PostgreSQL version: {version[0]}")
            
            cursor.execute("""
                SELECT current_setting('pool_mode'), 
                       current_database(), 
                       current_user;
            """)
            pool_mode, db, user = cursor.fetchone()
            print(f"\nPool mode: {pool_mode}")
            print(f"Database: {db}")
            print(f"User: {user}")
            
            return True
    except Exception as e:
        print(f"Connection failed: {str(e)}")
        return False

if __name__ == '__main__':
    test_db()
