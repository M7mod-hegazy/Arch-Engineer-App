from django import template
from django.utils import timezone
from django.utils.timesince import timeuntil
import datetime

register = template.Library()

@register.filter
def get_card_info(subject, current_date):
    card_class = "card h-100"
    text_class = ""
    days_left_text = ""

    if subject.date_limit:
        if subject.done:
            card_class = "card h-100 badge-success"
            text_class = "text-white"
        elif subject.date_limit < current_date:
            card_class = "card h-100 badge-danger"
            text_class = "text-white"
        else:
            days_left = timeuntil(subject.date_limit, current_date)
            days_left_text = f"Days Left: {days_left}"

    return {
        'card_class': card_class,
        'text_class': text_class,
        'days_left_text': days_left_text,
    }
