# In your app's urls.py
from django.urls import path
from . import views

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
    # Add the missing URL pattern for get_suggestions
    path('get-suggestions/', views.get_suggestions, name='get_suggestions'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
]