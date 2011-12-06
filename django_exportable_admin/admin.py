from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse


class ExportableAdmin(admin.ModelAdmin):
    """
    Subclass this for your own ModelAdmins to make their changelist exportable
    to CSV. Note: your subclasses cannot override change_list_template or you
    will not get the "Export CSV" button on your changelist page.
    """
    # use a custom changelist template which adds an "Export" button
    change_list_template = 'django_exportable_admin/change_list_exportable.html'

    # export 10,000 results by default
    export_queryset_limit = 10000

    export_formats = (
        (u'CSV', u','),
        (u'Pipe', u'|'),
    )

    def get_paginator(self, request, queryset, per_page, orphans=0, allow_empty_first_page=True):
        """
        When we are exporting, modify the paginator to return more results than
        the default admin changelist view.
        """
        if request.is_export_request:
            return self.paginator(queryset, self.export_queryset_limit, 0, True)
        return self.paginator(queryset, per_page, orphans, allow_empty_first_page)

    def get_export_buttons(self, request):
        app, mod = self.model._meta.app_label, self.model._meta.module_name
        return (
            ('Export %s' % format_name,
             reverse("admin:%s_%s_export_%s" % (app, mod, format_name.lower())))
             for format_name, delimiter in self.export_formats
        )

    def changelist_view(self, request, extra_context=None):
        """
        After 1.3, the changelist view returns a TemplateResponse, which we can
        use to greatly simplify this class. Instead of having to redefine a
        copy of the changelist_view to alter the template, we can simple change
        it after we get the TemplateResponse back.
        """
        if extra_context and extra_context['export_delimiter']:
            request.is_export_request = True
            response = super(ExportableAdmin, self).changelist_view(request, extra_context)
            # response is a TemplateResponse so we can change the template
            response.template_name = 'django_exportable_admin/change_list_csv.html'
            response['Content-Type'] = 'text/csv'
            response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(self.model._meta.verbose_name)
            return response
        extra_context = extra_context or {}
        extra_context.update({
            'export_buttons' : self.get_export_buttons(request),
        })
        return super(ExportableAdmin, self).changelist_view(request, extra_context)

    def get_urls(self):
        """
        Add a URL pattern for the export view.
        """
        urls = super(ExportableAdmin, self).get_urls()
        app, mod = self.model._meta.app_label, self.model._meta.module_name
        new_urls = [
            url(
                r'^export/%s$' % format_name.lower(),
                self.admin_site.admin_view(self.changelist_view),
                name="admin:%s_%s_export_%s" % (app, mod, format_name.lower()),
                kwargs={'extra_context':{'export_delimiter':delimiter}},
            )
            for format_name, delimiter in self.export_formats
        ]
        my_urls = patterns('', *new_urls)
        return my_urls + urls
