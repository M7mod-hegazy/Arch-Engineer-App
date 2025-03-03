from django import template
from django.templatetags.static import static
from urllib.parse import urlencode, urlparse, parse_qs
from django.conf import settings
from django.utils.safestring import mark_safe
import os

register = template.Library()

@register.simple_tag
def responsive_image(image_obj, width=None, height=None, lazy=True, class_name=""):
    """
    Renders an optimized responsive image with lazy loading and proper attributes
    
    Args:
        image_obj: An Image model instance or URL string
        width: Optional width attribute
        height: Optional height attribute
        lazy: Whether to enable lazy loading
        class_name: Optional CSS class names
    
    Returns:
        HTML markup for the responsive image
    """
    if not image_obj:
        # Return a placeholder if no image
        placeholder = f'<div class="no-image-placeholder {class_name}">No Image</div>'
        return mark_safe(placeholder)
    
    # Get image URL based on input type
    try:
        if hasattr(image_obj, 'url'):
            # It's a model with an image field
            url = image_obj.url
            
            # Try to get actual file dimensions if possible
            try:
                file_path = os.path.join(settings.MEDIA_ROOT, str(image_obj.image).lstrip('/'))
                if os.path.exists(file_path):
                    from PIL import Image
                    with Image.open(file_path) as img:
                        if not width:
                            width = img.width
                        if not height:
                            height = img.height
            except:
                # If we can't get dimensions from file, use defaults
                if not width:
                    width = 320
                if not height:
                    height = 240
        else:
            # Assume it's a string URL
            url = str(image_obj)
            if not width:
                width = 320
            if not height:
                height = 240
    except:
        # Fallback if something goes wrong
        placeholder = f'<div class="no-image-placeholder {class_name}">Image Error</div>'
        return mark_safe(placeholder)
    
    # Build attributes
    attrs = {
        'src': url,
        'class': class_name,
        'width': width,
        'height': height,
        'loading': 'lazy' if lazy else 'eager',
        'decoding': 'async',
    }
    
    # Convert to string attributes
    attr_str = ' '.join([f'{k}="{v}"' for k, v in attrs.items() if v])
    
    # Return the image tag
    return mark_safe(f'<img {attr_str} alt="Subject Image">')

@register.filter
def get_image_url(image_obj):
    """
    Returns just the URL from an image object
    Useful for responsive background images
    """
    if not image_obj:
        return ''
    
    try:
        if hasattr(image_obj, 'url'):
            return image_obj.url
        else:
            return str(image_obj)
    except:
        return ''

@register.filter
def thumbnail(image_obj, size='150x150'):
    """
    Returns a thumbnail URL for the given image
    """
    if not image_obj:
        return ''
    
    try:
        # If using sorl-thumbnail
        from sorl.thumbnail import get_thumbnail
        try:
            return get_thumbnail(image_obj, size, crop='center', quality=85).url
        except:
            if hasattr(image_obj, 'url'):
                return image_obj.url
            return str(image_obj)
    except ImportError:
        # Fallback if sorl-thumbnail is not installed
        if hasattr(image_obj, 'url'):
            return image_obj.url
        return str(image_obj)

@register.filter
def imagekit_thumbnail(image_obj, size='150x150'):
    """
    Returns a thumbnail URL using django-imagekit if available
    """
    if not image_obj:
        return ''
    
    try:
        from imagekit.processors import ResizeToFill
        from imagekit.cachefiles import ImageCacheFile
        
        width, height = map(int, size.split('x'))
        from imagekit import ImageSpec
        
        class Thumbnail(ImageSpec):
            processors = [ResizeToFill(width, height)]
        
        thumbnail = ImageCacheFile(Thumbnail(image_obj))
        thumbnail.generate()
        return thumbnail.url
    except ImportError:
        # Fallback if imagekit is not installed
        if hasattr(image_obj, 'url'):
            return image_obj.url
        return str(image_obj)

@register.filter
def add_query_params(url, params):
    """
    Add query parameters to a URL
    
    Usage: {{ url|add_query_params:params_dict }}
    """
    if not params:
        return url
        
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # Update with new params
    for key, value in params.items():
        query_params[key] = [value]
    
    # Rebuild query string
    encoded_params = urlencode(query_params, doseq=True)
    
    # Handle URLs with or without existing query parameters
    if parsed_url.query:
        return url.replace(parsed_url.query, encoded_params)
    else:
        return f"{url}{'?' if '?' not in url else '&'}{encoded_params}"

@register.filter
def with_cache_buster(url):
    """
    Add a cache busting parameter to static files
    
    Usage: {{ "css/style.css"|with_cache_buster }}
    """
    import time
    timestamp = int(time.time())
    return add_query_params(url, {'v': timestamp}) 