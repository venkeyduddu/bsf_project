from django import template
from datetime import date, time, datetime
from dateutil.parser import parse
import urllib

register = template.Library()


@register.filter
def filter_date(value, arg):
    date_obj = parse(value)
    if arg == "d":
        return date_obj.strftime("%d")
    elif arg == "month":
        return date_obj.strftime("%B")
    elif arg == "year":
        return date_obj.strftime("%Y")
    elif arg == "time":
        return date_obj.strftime("%H:%M %p")
    else:
        return 0


@register.filter
def get_encoded_dict(data_dict):
    return urllib.parse.urlencode(data_dict)


@register.filter
def filter_yes_no(value, arg):
    if ')' in value and '(' in value:
        if arg == "runs":
            return value.replace(')', '').split('(')[1]
        elif arg == "yes_no":
            return value.replace(')', '').split('(')[0]
        else:
            return value
    return '---'
