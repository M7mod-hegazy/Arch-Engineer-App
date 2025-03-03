from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
import boto3
from botocore.config import Config
import urllib.parse
from django.core.cache import cache

class CacheBustingStaticFilesStorage(ManifestStaticFilesStorage):
    def url(self, name, *args, **kwargs):
        if name.endswith('.css'):
            url = super().url(name, *args, **kwargs)
            return f"{url}?v={settings.CSS_VERSION}"
        return super().url(name, *args, **kwargs)

class SupabaseStorage(S3Boto3Storage):
    """Custom storage class for Supabase with performance optimizations"""
    access_key = settings.AWS_ACCESS_KEY_ID
    secret_key = settings.AWS_SECRET_ACCESS_KEY
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    location = ''
    file_overwrite = False
    default_acl = 'public-read'
    custom_domain = None
    cloudfront_domain = None
    
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'access_key': self.access_key,
            'secret_key': self.secret_key,
            'bucket_name': self.bucket_name,
            'endpoint_url': settings.AWS_S3_ENDPOINT_URL,
            'region_name': settings.AWS_S3_REGION_NAME,
            'use_ssl': True,
            'verify': True,
            'addressing_style': 'path',
            'signature_version': 's3v4'
        })
        super().__init__(**kwargs)

    def url(self, name):
        """
        Generate direct URL for Supabase storage with caching
        """
        # Cache the URL to avoid repeated string operations
        cache_key = f'supabase_url_{name}'
        cached_url = cache.get(cache_key)
        if cached_url:
            return cached_url
            
        # URL encode the name to handle special characters
        encoded_name = urllib.parse.quote(name)
        
        # Generate the URL using the bucket name from settings
        url = f"{settings.AWS_S3_ENDPOINT_URL.replace('/s3', '')}/object/public/{self.bucket_name}/{encoded_name}"
        
        # Cache the URL for 1 hour (3600 seconds)
        cache.set(cache_key, url, 3600)
        
        return url
