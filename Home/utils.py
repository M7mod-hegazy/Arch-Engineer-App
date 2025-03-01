import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import connection

def test_s3_connection():
    """Test S3 storage connection"""
    try:
        test_content = ContentFile(b'test content')
        path = default_storage.save('test/test.txt', test_content)
        url = default_storage.url(path)
        
        # Verify the file exists
        exists = default_storage.exists(path)
        
        # Clean up
        default_storage.delete(path)
        
        return {
            'success': True,
            'url': url,
            'exists': exists
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def test_supabase_connection():
    """Test both database and storage connections"""
    results = {
        'database': False,
        'storage': False,
        'errors': []
    }
    
    # Test database
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        results['database'] = True
    except Exception as e:
        results['errors'].append(f'Database error: {str(e)}')
    
    # Test storage using S3 connection
    storage_test = test_s3_connection()
    results['storage'] = storage_test['success']
    if not storage_test['success']:
        results['errors'].append(f'Storage error: {storage_test.get("error", "Unknown error")}')
    
    return results

result = test_s3_connection()
print(result)
