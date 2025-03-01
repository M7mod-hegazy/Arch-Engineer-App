from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
import boto3
from botocore.config import Config

class CacheBustingStaticFilesStorage(ManifestStaticFilesStorage):
    def url(self, name, *args, **kwargs):
        if name.endswith('.css'):
            url = super().url(name, *args, **kwargs)
            return f"{url}?v={settings.CSS_VERSION}"
        return super().url(name, *args, **kwargs)

class SupabaseStorage(S3Boto3Storage):
    """Custom storage class for Supabase"""
    access_key = '873e9bb211a47d1b66e69313a2d3fd10'
    secret_key = '7d44b01faf9a3ab6d0e293e61da73ab4894cdd343fcc23107e854aff13970491'
    bucket_name = 'images'
    location = ''
    file_overwrite = False
    default_acl = 'public-read'
    
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'access_key': self.access_key,
            'secret_key': self.secret_key,
            'bucket_name': self.bucket_name,
            'endpoint_url': 'https://tfktuezhiykprdwgiamd.supabase.co/storage/v1/s3',
            'region_name': 'us-east-1',
            'use_ssl': True,
            'verify': False,
            'addressing_style': 'path',
            'signature_version': 's3v4'
        })
        super().__init__(**kwargs)

    def url(self, name):
        """Generate direct URL for Supabase storage"""
        return f"https://tfktuezhiykprdwgiamd.supabase.co/storage/v1/object/public/{self.bucket_name}/{name}"
