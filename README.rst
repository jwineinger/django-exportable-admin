=======================
django-exportable-admin
=======================
This app provides a ModelAdmin which you can subclass in order to allow your
changelist view to be exported to CSV.  This will add an "Export CSV" button to
the top-right of the changelist. Clicking this button will export a CSV
containing the same columns and headings as your changelist view.  By default,
up to 10,000 rows will be exported, though this can be changed easily.

Django > 1.3 is required, at which point the standard changelist_view() returns
a TemplateResponse. This allows us to change the template used after the
response is created, so that we can output CSV instead of the standard HTML
view.  Django <= 1.3 requires a previous version of this app in which the
changelist_view code is duplicated and modified slightly to change the template
and setup the response for download instead of display.

Note: if you alter 'change_list_template' on your ModelAdmin subclass, the
"Export CSV" button will not appear. You will need to add it manually to your
template or link to the correct url (admin:myapp_mymodel_export) by some other
means.

Examples
--------

Simple example:
~~~~~~~~~~~~~~~

::

    # myapp/admin.py
    from django.contrib import admin
    from django_exportable_admin.admin import ExportableAdmin
    from models import MyModel

    class MyModelAdmin(ExportableAdmin):
        list_display = ('field1','field2','field3')
    admin.site.register(MyModel, MyModelAdmin)

Complex example:
~~~~~~~~~~~~~~~~

::

    # myapp/admin.py
    from django.contrib import admin
    from django_exportable_admin.admin import ExportableAdmin
    from models import MyModel

    class MyModelAdmin(ExportableAdmin):
        list_display = ('field1','field2','calculated_field')

        # adjust the number of results
        export_queryset_limit = 100

        def calculated_field(self, obj):
            return u"%.3f" % obj.float_field / 33.7
        calculated_field.short_description = 'Arbitrary Title'
    admin.site.register(MyModel, MyModelAdmin)
