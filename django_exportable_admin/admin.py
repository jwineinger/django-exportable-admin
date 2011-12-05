from django.contrib import admin
from django.conf.urls.defaults import patterns, url
from django.template.defaultfilters import slugify
from django.contrib.admin import helpers
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext
from django.utils.encoding import force_unicode
from django import template
from django.shortcuts import render_to_response
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect


class IncorrectLookupParameters(Exception):
    pass

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
        Override the changelist view so that we can provide the URL name to
        setup the export button in the customized template.
        """
        info = self.model._meta.app_label, self.model._meta.module_name
        extra_context = extra_context or {}
        extra_context['app_export_url'] = "admin:%s_%s_export" % info
        return super(ExportableAdmin, self).changelist_view(request, extra_context)

    def changelist_export_view(self, request, extra_context=None):
        """
        This method is nearly an exact copy of the standard changelist_view()
        method, except that we change the template, response mimetype, and
        response content-disposition so that it sends the response as a
        download.
        """
        from django.contrib.admin.views.main import ERROR_FLAG
        opts = self.model._meta
        app_label = opts.app_label
        if not self.has_change_permission(request, None):
            raise PermissionDenied

        # Check actions to see if any are available on this changelist
        actions = self.get_actions(request)

        # Remove action checkboxes if there aren't any actions available.
        list_display = list(self.list_display)
        if not actions:
            try:
                list_display.remove('action_checkbox')
            except ValueError:
                pass

        ChangeList = self.get_changelist(request)
        try:
            cl = ChangeList(request, self.model, list_display, self.list_display_links,
                self.list_filter, self.date_hierarchy, self.search_fields,
                self.list_select_related, self.list_per_page, self.list_editable, self)
        except IncorrectLookupParameters:
            # Wacky lookup parameters were given, so redirect to the main
            # changelist page, without parameters, and pass an 'invalid=1'
            # parameter via the query string. If wacky parameters were given
            # and the 'invalid=1' parameter was already in the query string,
            # something is screwed up with the database, so display an error
            # page.
            if ERROR_FLAG in request.GET.keys():
                return render_to_response('admin/invalid_setup.html', {'title': _('Database error')})
            return HttpResponseRedirect(request.path + '?' + ERROR_FLAG + '=1')

        # If the request was POSTed, this might be a bulk action or a bulk
        # edit. Try to look up an action or confirmation first, but if this
        # isn't an action the POST will fall through to the bulk edit check,
        # below.
        action_failed = False
        selected = request.POST.getlist(helpers.ACTION_CHECKBOX_NAME)

        # Actions with no confirmation
        if (actions and request.method == 'POST' and
                'index' in request.POST and '_save' not in request.POST):
            if selected:
                response = self.response_action(request, queryset=cl.get_query_set())
                if response:
                    return response
                else:
                    action_failed = True
            else:
                msg = _("Items must be selected in order to perform "
                        "actions on them. No items have been changed.")
                self.message_user(request, msg)
                action_failed = True

        # If we're allowing changelist editing, we need to construct a formset
        # for the changelist given all the fields to be edited. Then we'll
        # use the formset to validate/process POSTed data.
        formset = cl.formset = None

        # Handle POSTed bulk-edit data.
        if (request.method == "POST" and cl.list_editable and
                '_save' in request.POST and not action_failed):
            FormSet = self.get_changelist_formset(request)
            formset = cl.formset = FormSet(request.POST, request.FILES, queryset=cl.result_list)
            if formset.is_valid():
                changecount = 0
                for form in formset.forms:
                    if form.has_changed():
                        obj = self.save_form(request, form, change=True)
                        self.save_model(request, obj, form, change=True)
                        form.save_m2m()
                        change_msg = self.construct_change_message(request, form, None)
                        self.log_change(request, obj, change_msg)
                        changecount += 1

                if changecount:
                    if changecount == 1:
                        name = force_unicode(opts.verbose_name)
                    else:
                        name = force_unicode(opts.verbose_name_plural)
                    msg = ungettext("%(count)s %(name)s was changed successfully.",
                                    "%(count)s %(name)s were changed successfully.",
                                    changecount) % {'count': changecount,
                                                    'name': name,
                                                    'obj': force_unicode(obj)}
                    self.message_user(request, msg)

                return HttpResponseRedirect(request.get_full_path())
        # Handle GET -- construct a formset for display.
        elif cl.list_editable:
            FormSet = self.get_changelist_formset(request)
            formset = cl.formset = FormSet(queryset=cl.result_list)

        # Build the list of media to be used by the formset.
        if formset:
            media = self.media + formset.media
        else:
            media = self.media

        # Build the action form and populate it with available actions.
        if actions:
            action_form = self.action_form(auto_id=None)
            action_form.fields['action'].choices = self.get_action_choices(request)
        else:
            action_form = None

        selection_note_all = ungettext('%(total_count)s selected',
            'All %(total_count)s selected', cl.result_count)

        context = {
            'module_name': force_unicode(opts.verbose_name_plural),
            'selection_note': _('0 of %(cnt)s selected') % {'cnt': len(cl.result_list)},
            'selection_note_all': selection_note_all % {'total_count': cl.result_count},
            'title': cl.title,
            'is_popup': cl.is_popup,
            'cl': cl,
            'media': media,
            'has_add_permission': self.has_add_permission(request),
            'root_path': self.admin_site.root_path,
            'app_label': app_label,
            'action_form': action_form,
            'actions_on_top': self.actions_on_top,
            'actions_on_bottom': self.actions_on_bottom,
            'actions_selection_counter': self.actions_selection_counter,
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        response = render_to_response(
            'django_exportable_admin/change_list_csv.html',
            context,
            context_instance=context_instance,
        )
        response['Content-Type'] = 'text/csv'
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % slugify(self.model._meta.verbose_name)
        return response


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
                self.admin_site.admin_view(self.changelist_export_view),
                name="%s_%s_export" % info,
            )
        )
        return my_urls + urls
