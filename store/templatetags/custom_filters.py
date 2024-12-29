from django import template
from django.db.models import Avg

register = template.Library()

@register.filter
def average_rating(ratings):
    average = ratings.aggregate(Avg('rating'))['rating__avg']
    return average if average else 0
