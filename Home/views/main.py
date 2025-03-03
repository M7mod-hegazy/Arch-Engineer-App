from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory, inlineformset_factory
from ..models import Subject, Image
from ..forms import SubjectForm
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q, Count, Case, When, IntegerField, Exists, OuterRef
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import DatabaseError, connection
from django.utils import timezone
import datetime
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
import logging
import sys

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET", "HEAD"])
def health_check(request):
    """Super lightweight health check endpoint."""
    logger.info(f"Health check started - Method: {request.method}, Path: {request.path}")
    
    # Return immediately with 200 OK
    response = HttpResponse(
        content="OK",
        status=200,
        content_type="text/plain",
        charset="utf-8"
    )
    
    # Set headers to prevent caching
    response["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, HEAD"
    
    logger.info("Health check completed successfully")
    return response

@cache_page(60 * 5)  # Cache for 5 minutes
def image_list(request):
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    sort_by = request.GET.get('sort_by', 'customer_asc')
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)
    
    # Define the query once and reuse it
    now = timezone.now()
    
    # Base queryset with prefetched images to avoid N+1 queries
    subjects_list = Subject.objects.prefetch_related('images')
    
    # Apply search filter
    if query:
        subjects_list = subjects_list.filter(
            Q(customer__icontains=query) | Q(comment__icontains=query)
        )

    # Apply status filter
    if status_filter and status_filter != 'all':
        if status_filter == 'done':
            subjects_list = subjects_list.filter(done=True)
        elif status_filter == 'waiting':
            subjects_list = subjects_list.filter(
                Q(done=False) & 
                (Q(date_limit__gt=now) | Q(date_limit__isnull=True))
            )
        elif status_filter == 'expired':
            subjects_list = subjects_list.filter(
                done=False,
                date_limit__lte=now
            )

    # Apply sorting
    sort_field = sort_by.replace('_asc', '').replace('_desc', '')
    sort_direction = '-' if sort_by.endswith('_desc') else ''
    
    if sort_field in ['customer', 'date_posted', 'date_limit', 'price']:
        subjects_list = subjects_list.order_by(f'{sort_direction}{sort_field}')

    # Optimize: Pre-compute all status counts in a single query
    status_counts = Subject.objects.aggregate(
        total_count=Count('id'),
        done_count=Count(Case(
            When(done=True, then=1),
            output_field=IntegerField()
        )),
        waiting_count=Count(Case(
            When(done=False, date_limit__gt=now, then=1),
            When(done=False, date_limit__isnull=True, then=1),
            output_field=IntegerField()
        )),
        expired_count=Count(Case(
            When(done=False, date_limit__lte=now, then=1),
            output_field=IntegerField()
        ))
    )

    # Get items per page from request or use default (9)
    items_per_page = int(request.GET.get('per_page', 9))
    
    # Pagination
    paginator = Paginator(subjects_list, items_per_page)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Update status for each subject in memory to avoid additional queries
    for subject in page_obj:
        if subject.done:
            subject.status = 'done'
        elif subject.date_limit and subject.date_limit < now:
            subject.status = 'expired'
        else:
            subject.status = 'waiting'

    context = {
        'page_obj': page_obj,
        'subjects': page_obj,
        'sort_by': sort_by,
        'status_filter': status_filter,
        'query': query,
        'total_count': status_counts['total_count'],
        'done_count': status_counts['done_count'],
        'waiting_count': status_counts['waiting_count'],
        'expired_count': status_counts['expired_count'],
        'per_page': items_per_page,
    }
    
    return render(request, 'home.html', context)

def add_subject(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            
            # Handle multiple image uploads
            for image in request.FILES.getlist('images'):
                Image.objects.create(
                    subject=subject,
                    image=image
                )
            return redirect('image_list')
    else:
        form = SubjectForm()
    
    return render(request, 'add_subject.html', {'form': form})

def edit_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            subject = form.save()
            
            # Handle multiple image uploads
            for image in request.FILES.getlist('images'):
                Image.objects.create(
                    subject=subject,
                    image=image
                )
            return redirect('image_list')
    else:
        form = SubjectForm(instance=subject)
    
    return render(request, 'edit_subject.html', {
        'form': form,
        'subject': subject
    })

def delete_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject.delete()
        return redirect('image_list')
    return render(request, 'delete_subject.html', {'subject': subject})

def delete_image(request, pk):
    image = get_object_or_404(Image, pk=pk)
    if request.method == 'POST':
        image.delete()
        return redirect('edit_subject', pk=image.subject.pk)
    return render(request, 'delete_image.html', {'image': image})

@require_http_methods(["POST"])
def delete_image_ajax(request, pk):
    """
    AJAX view for deleting images without page refresh
    """
    try:
        image = get_object_or_404(Image, pk=pk)
        subject_id = image.subject.id  # Store subject ID before deletion
        image.delete()
        
        # Return subject ID so frontend can update related elements if needed
        return JsonResponse({
            'status': 'success',
            'message': 'Image deleted successfully',
            'subject_id': subject_id
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def toggle_image_done(request, pk):
    image = get_object_or_404(Image, pk=pk)
    image.done = not image.done
    image.save()
    image.subject.update_done_status()
    return redirect('image_list')

def toggle_subject_done(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    subject.done = not subject.done
    subject.save()
    subject.update_done_status()
    return redirect('image_list')

def search(request):
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'date_posted')  # Default sort by date posted
    sort_dir = request.GET.get('dir', 'desc')  # Default direction is descending
    
    if query:
        subjects = Subject.objects.filter(
            Q(customer__icontains=query) | 
            Q(comment__icontains=query)
        )
    else:
        subjects = Subject.objects.all()
    
    # Apply sorting
    if sort_dir == 'asc':
        order_by = sort_by
    else:
        order_by = f'-{sort_by}'
    
    subjects = subjects.order_by(order_by)
    
    # Paginate the results - 2 cards per page
    paginator = Paginator(subjects, 2)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'sort_by': sort_by,
        'sort_dir': sort_dir,
    }
    
    return render(request, 'home.html', context)

@cache_page(60 * 5)  # Cache for 5 minutes
def get_suggestions(request):
    """
    AJAX view for search suggestions
    """
    term = request.GET.get('term', '')
    
    if len(term) > 1:
        # Get unique customer names and comments that match the search term
        customer_suggestions = Subject.objects.filter(
            customer__icontains=term
        ).values_list('customer', flat=True).distinct()[:5]
        
        comment_suggestions = Subject.objects.filter(
            comment__icontains=term
        ).values_list('comment', flat=True).distinct()[:3]
        
        # Combine and deduplicate suggestions
        all_suggestions = list(customer_suggestions) + list(comment_suggestions)
        unique_suggestions = list(set(all_suggestions))[:8]  # Limit to 8 suggestions
        
        return JsonResponse({'suggestions': unique_suggestions})
    
    return JsonResponse({'suggestions': []})

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html') 