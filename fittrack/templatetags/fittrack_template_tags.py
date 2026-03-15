from django import template
from fittrack.models import Exercise

register = template.Library()

@register.inclusion_tag('fittrack/exercises.html')
def get_exercise_list(current_category=None):
    return {'exercises': Exercise.objects.all()}