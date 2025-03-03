/**
 * Gallery functionality for image viewing
 * This file handles the image gallery modal and navigation
 */

// Gallery state variables
let currentGallery = null;
let currentIndex = 0;
let zoomLevel = 1;
let rotation = 0;

// Open the gallery modal
window.openGallery = function(img) {
    const modal = document.getElementById('galleryModal');
    const modalImg = document.getElementById('galleryImg');
    const galleryName = img.dataset.gallery;
    const index = parseInt(img.dataset.index);
    
    // Get all images in this gallery
    const galleryImages = document.querySelectorAll(`[data-gallery="${galleryName}"]`);
    
    // Filter out images that have failed to load
    currentGallery = Array.from(galleryImages).filter(image => {
        return !image.classList.contains('image-error');
    });
    
    // If the gallery is empty after filtering, don't open
    if (currentGallery.length === 0) {
        console.warn('No valid images to display in gallery');
        return;
    }
    
    // Adjust index if needed
    currentIndex = Math.min(index, currentGallery.length - 1);
    
    // Reset zoom and rotation
    zoomLevel = 1;
    rotation = 0;
    
    // Display the image
    modalImg.src = img.src;
    modalImg.style.transform = `scale(${zoomLevel}) rotate(${rotation}deg)`;
    modal.style.display = 'block';
    
    // Update navigation
    updateGalleryNavigation();
    
    // Prevent scrolling on body when gallery is open
    document.body.style.overflow = 'hidden';
};

// Close the gallery modal
window.closeGallery = function() {
    document.getElementById('galleryModal').style.display = 'none';
    document.body.style.overflow = 'auto'; // Restore scrolling
};

// Navigate to previous image
window.prevImage = function() {
    if (currentIndex > 0) {
        currentIndex--;
        document.getElementById('galleryImg').src = currentGallery[currentIndex].src;
        updateGalleryNavigation();
        resetImageTransform();
    }
};

// Navigate to next image
window.nextImage = function() {
    if (currentIndex < currentGallery.length - 1) {
        currentIndex++;
        document.getElementById('galleryImg').src = currentGallery[currentIndex].src;
        updateGalleryNavigation();
        resetImageTransform();
    }
};

// Zoom in
window.zoomIn = function() {
    zoomLevel += 0.2;
    updateImageTransform();
};

// Zoom out
window.zoomOut = function() {
    if (zoomLevel > 0.4) {
        zoomLevel -= 0.2;
        updateImageTransform();
    }
};

// Rotate image
window.rotateImage = function() {
    rotation += 90;
    updateImageTransform();
};

// Update the image transform
function updateImageTransform() {
    const modalImg = document.getElementById('galleryImg');
    modalImg.style.transform = `scale(${zoomLevel}) rotate(${rotation}deg)`;
}

// Reset image transform to default
function resetImageTransform() {
    zoomLevel = 1;
    rotation = 0;
    updateImageTransform();
}

// Update gallery navigation UI elements
function updateGalleryNavigation() {
    // Update navigation buttons visibility
    document.querySelector('.gallery-prev').style.visibility = currentIndex > 0 ? 'visible' : 'hidden';
    document.querySelector('.gallery-next').style.visibility = currentIndex < currentGallery.length - 1 ? 'visible' : 'hidden';
    
    // Update navigation dots
    const nav = document.querySelector('.gallery-navigation');
    nav.innerHTML = '';
    
    // Only add navigation dots if more than one image
    if (currentGallery.length > 1) {
        currentGallery.forEach((img, idx) => {
            const dot = document.createElement('span');
            dot.className = 'gallery-dot' + (idx === currentIndex ? ' active' : '');
            dot.onclick = () => {
                currentIndex = idx;
                document.getElementById('galleryImg').src = currentGallery[idx].src;
                updateGalleryNavigation();
                resetImageTransform();
            };
            nav.appendChild(dot);
        });
    }
}

// Set up event listeners when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && document.getElementById('galleryModal').style.display === 'block') {
            closeGallery();
        }
    });
    
    // Close on click outside image
    document.getElementById('galleryModal')?.addEventListener('click', function(e) {
        if (e.target === this) {
            closeGallery();
        }
    });
    
    // Arrow key navigation
    document.addEventListener('keydown', function(e) {
        if (document.getElementById('galleryModal').style.display !== 'block') return;
        
        if (e.key === 'ArrowLeft') {
            prevImage();
        } else if (e.key === 'ArrowRight') {
            nextImage();
        }
    });
    
    // Handle image error events for all gallery images
    document.querySelectorAll('.gallery-img').forEach(img => {
        img.addEventListener('error', function() {
            console.warn('Image failed to load:', this.src);
            this.classList.add('image-error');
            
            // Handle slider item
            const sliderItem = this.closest('.slider-item');
            if (sliderItem) {
                sliderItem.classList.add('error-image');
                sliderItem.innerHTML = `
                    <div class="image-error-placeholder">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Image unavailable</p>
                    </div>
                `;
            }
        });
    });
}); 