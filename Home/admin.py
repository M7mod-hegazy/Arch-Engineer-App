from django.contrib import admin
from .models import Subject, Image

class ImageInline(admin.TabularInline):
    model = Image
    extra = 1

class SubjectAdmin(admin.ModelAdmin):
    inlines = [ImageInline]

admin.site.register(Subject, SubjectAdmin)
admin.site.register(Image)

