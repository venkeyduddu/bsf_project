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
