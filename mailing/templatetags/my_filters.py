# В вашем файле templatetags/my_custom_filters.py

from django import template

register = template.Library()


@register.filter
def get_msgs_stats_for_mailing(dictionary: dict[int, dict[str, int]], mailing) -> dict[str, int]:
    return dictionary[mailing.id]


@register.filter
def get_spec_msgs_stats(dictionary: dict[str, int], msgs_type: str) -> int:
    return dictionary[msgs_type]
