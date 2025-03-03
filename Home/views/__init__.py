# This file makes the views directory a Python package 

from .main import (
    health_check,
    image_list,
    add_subject,
    edit_subject,
    delete_subject,
    delete_image,
    delete_image_ajax,
    toggle_image_done,
    toggle_subject_done,
    search,
    get_suggestions,
    about_view,
    contact_view,
) 