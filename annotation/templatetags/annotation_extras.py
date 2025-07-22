from django import template
register = template.Library()

@register.filter
def substr(value, args):
    try:
        start, end = map(int, args.split(','))
        return value[start:end]
    except Exception:
        return ''