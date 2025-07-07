from django import template

register = template.Library()


@register.filter
def duration(duration_value):
    total_seconds = int(duration_value.total_seconds())
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60

    if h > 0:
        if m > 0:
            return f"{h}h{m:02d}"
        return f"{h}h"
    return f"{m}min" if m > 0 else "0min"
