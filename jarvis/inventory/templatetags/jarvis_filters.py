from django import template
register = template.Library()
from datetime import datetime, timedelta

#useful for retrieving dictionary values whose keys have spaces
@register.filter
def get(mapping, key):
    return mapping.get(key, '')

@register.simple_tag
def link_status(link_list):
    html = ["<span class='"]
    tooltip = ""
    if link_list and len(link_list) > 0:
        link = link_list[-1]
        if link.last_checked + timedelta(minutes=10) <= datetime.now():
            #it has been too long since this device was last checked
            html.append("glyphicon glyphicon-question-sign jarv-oldlink")
            tooltip = "Has not been queried recently"
        elif link.status:
            html.append("glyphicon glyphicon-ok-sign jarv-online")
            tooltip = "Was seen online recently"
        else:
            html.append("glyphicon glyphicon-minus-sign jarv-offline")
            tooltip = "Has not responded to recent queries"
    html.append("' aria-hidden='true' data-toggle='tooltip' "
        "data-placement='left' title='"+tooltip+"'></span>")
    return "".join(html)
