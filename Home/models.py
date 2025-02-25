from django.db import models
from django.utils import timezone
from datetime import timedelta

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
    image = models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return str(self.image)
