from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.template.defaultfilters import slugify


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

    def get_paginator(self, request, queryset, per_page, orphans=0, allow_empty_first_page=True):
        """
        When we are exporting, modify the paginator to return more results than
        the default admin changelist view.
        """
        if request.path.count('export'):
            return self.paginator(queryset, self.export_queryset_limit, 0, True)
        return self.paginator(queryset, per_page, orphans, allow_empty_first_page)

    def changelist_view(self, request, extra_context=None):
        """
        After 1.3, the changelist view returns a TemplateResponse, which we can
        use to greatly simplify this class. Instead of having to redefine a
        copy of the changelist_view to alter the template, we can simple change
        it after we get the TemplateResponse back.
        """
        if request.path.count('export'):
            response = super(ExportableAdmin, self).changelist_view(request, extra_context)
            # response is a TemplateResponse so we can change the template
            response.template_name = 'django_exportable_admin/change_list_csv.html'
            response['Content-Type'] = 'text/csv'
            response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(self.model._meta.verbose_name)
            return response
        info = self.model._meta.app_label, self.model._meta.module_name
        extra_context = extra_context or {}
        extra_context['app_export_url'] = "admin:%s_%s_export" % info
        return super(ExportableAdmin, self).changelist_view(request, extra_context)

    def get_urls(self):
        """
        Add a URL pattern for the export view.
        """
        urls = super(ExportableAdmin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.module_name
        my_urls = patterns(
            '',
            url(
                r'^export/$',
                self.admin_site.admin_view(self.changelist_view),
                name="%s_%s_export" % info,
            )
        )
        return my_urls + urls
