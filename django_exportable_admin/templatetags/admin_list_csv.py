from django.template import Library
from django.contrib.admin.templatetags.admin_list import result_headers, results

register = Library()


@register.inclusion_tag("django_exportable_admin/change_list_results_csv.html",
                        takes_context=True)
def result_list(context):
    """
    Displays the headers and data list together
    """
    cl = context['cl']
    return {'cl': cl,
            'result_headers': list(result_headers(cl)),
            'results': list(results(cl)),
            'export_delimiter' : context['export_delimiter'],
           }
