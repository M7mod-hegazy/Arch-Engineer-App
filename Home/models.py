from django.db import models
from django.utils import timezone
from datetime import timedelta
from .storage import SupabaseStorage
from django.utils.text import slugify
import os

class Subject(models.Model):
    customer = models.CharField(max_length=100, blank=True)
    price = models.IntegerField(default=0)
    comment = models.TextField(blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)
    done = models.BooleanField(default=False)
    date_limit = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, default='waiting')  # done, waiting, expired

    def __str__(self):
        return self.customer
    
    def update_done_status(self):
        if self.done:
            self.status = 'done'
        elif self.date_limit and self.date_limit < timezone.now():
            self.status = 'expired'
        else:
            self.status = 'waiting'
        self.save()

class Image(models.Model):
    subject = models.ForeignKey(Subject, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='',  # Empty upload_to
        storage=SupabaseStorage(),
        blank=True,
        null=True
    )

    class Meta:
        # Add unique constraint to prevent duplicate images for same subject
        unique_together = ('subject', 'image')

    def save(self, *args, **kwargs):
        if self.image:
            filename = os.path.basename(self.image.name)
            name, ext = os.path.splitext(filename)
            # Add timestamp to ensure unique filenames
            timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
            self.image.name = f"{slugify(name)}_{timestamp}{ext}".lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.subject.customer}"
    
    def delete(self, *args, **kwargs):
        self.image.delete(save=False)
        super().delete(*args, **kwargs)

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return ''
