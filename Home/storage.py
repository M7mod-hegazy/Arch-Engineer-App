from django.contrib.staticfiles.storage import ManifestStaticFilesStorage
from django.conf import settings

class CacheBustingStaticFilesStorage(ManifestStaticFilesStorage):
    def url(self, name, *args, **kwargs):
        if name.endswith('.css'):
            url = super().url(name, *args, **kwargs)
            return f"{url}?v={settings.CSS_VERSION}"
        return super().url(name, *args, **kwargs)
