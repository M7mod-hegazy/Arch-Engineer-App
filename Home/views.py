from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory, inlineformset_factory
from .models import Subject, Image
from .forms import SubjectForm, ImageForm
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import DatabaseError
from django.utils import timezone
import datetime

def image_list(request):
    # Get all subjects initially
    subjects_list = Subject.objects.all()
    
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    sort_by = request.GET.get('sort_by', 'customer_asc')
    query = request.GET.get('q', '')
    page = request.GET.get('page', 1)

    # Apply search filter
    if query:
        subjects_list = subjects_list.filter(
            Q(customer__icontains=query) | Q(comment__icontains=query)
        )

    # Apply status filter
    if status_filter and status_filter != 'all':
        now = timezone.now()
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

    # Update status for each subject
    now = timezone.now()
    for subject in subjects_list:
        if subject.done:
            subject.status = 'done'
        elif subject.date_limit and subject.date_limit < now:
            subject.status = 'expired'
        else:
            subject.status = 'waiting'

    # Pagination
    paginator = Paginator(subjects_list, 2)
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Get counts for each status
    now = timezone.now()
    total_count = Subject.objects.count()
    done_count = Subject.objects.filter(done=True).count()
    expired_count = Subject.objects.filter(
        done=False,
        date_limit__lte=now
    ).count()
    waiting_count = Subject.objects.filter(
        done=False
    ).filter(
        Q(date_limit__gt=now) | Q(date_limit__isnull=True)
    ).count()

    context = {
        'page_obj': page_obj,
        'subjects': page_obj,
        'sort_by': sort_by,
        'status_filter': status_filter,
        'query': query,
        'total_count': total_count,
        'done_count': done_count,
        'waiting_count': waiting_count,
        'expired_count': expired_count,
    }
    
    return render(request, 'home.html', context)

def add_subject(request):
    ImageFormSet = inlineformset_factory(Subject, Image, form=ImageForm, extra=1, can_delete=True)

    if request.method == 'POST':
        subject_form = SubjectForm(request.POST)
        if subject_form.is_valid():
            subject = subject_form.save()
            for key in request.FILES:
                image = Image(
                    subject=subject,
                    image=request.FILES[key],
                    title=request.POST.get('title'),
                    comment=request.POST.get('comment'),
                    date_limit=request.POST.get('date_limit')
                )
                image.save()
            subject.update_done_status()
            return redirect('image_list')
    else:
        subject_form = SubjectForm()
        return render(request, 'add_subject.html', {'subject_form': subject_form})

def edit_subject(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        subject_form = SubjectForm(request.POST, instance=subject)
        if subject_form.is_valid():
            subject_form.save()
            for key in request.FILES:
                image = Image(
                    subject=subject,
                    image=request.FILES[key],
                    title=request.POST.get('title'),
                    comment=request.POST.get('comment'),
                    date_limit=request.POST.get('date_limit')
                )
                image.save()
            subject.update_done_status()
            return redirect('image_list')
    else:
        subject_form = SubjectForm(instance=subject)
    return render(request, 'edit_subject.html', {'subject_form': subject_form, 'subject': subject})

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

def delete_image_ajax(request, pk):
    """
    AJAX view for deleting images without page refresh
    """
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            image = get_object_or_404(Image, pk=pk)
            subject_pk = image.subject.pk
            image.delete()
            # Update subject status after image deletion
            subject = Subject.objects.get(pk=subject_pk)
            subject.update_done_status()
            return JsonResponse({'status': 'success', 'message': 'Image deleted successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

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