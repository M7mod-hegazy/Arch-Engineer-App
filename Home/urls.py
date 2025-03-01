# In your app's urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.image_list, name='image_list'),
    path('add/', views.add_subject, name='add_subject'),
    path('edit/<int:pk>/', views.edit_subject, name='edit_subject'),
    path('delete/<int:pk>/', views.delete_subject, name='delete_subject'),
    path('delete-image/<int:pk>/', views.delete_image, name='delete_image'),
    path('delete-image-ajax/<int:pk>/', views.delete_image_ajax, name='delete_image_ajax'),
    path('toggle-image/<int:pk>/', views.toggle_image_done, name='toggle_image_done'),
    path('toggle-subject/<int:pk>/', views.toggle_subject_done, name='toggle_subject_done'),
    path('search/', views.search, name='search'),
    path('get-suggestions/', views.get_suggestions, name='get_suggestions'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('image/<int:pk>/delete/', views.delete_image_ajax, name='delete_image_ajax'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)