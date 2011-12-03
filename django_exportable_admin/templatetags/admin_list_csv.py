from django.template import Library
from django.contrib.admin.templatetags.admin_list import result_headers, results

register = Library()


@register.inclusion_tag("django_exportable_admin/change_list_results_csv.html")
def result_list(cl):
    """
    Displays the headers and data list together
    """
    headers = list(result_headers(cl))
    return {'cl': cl,
            'result_headers': headers,
            'results': list(results(cl))}
