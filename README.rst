=======================
django-exportable-admin
=======================
django-exportable-admin provides ModelAdmin base classes which you can use to 
add delimited-format (such as CSV) export functionality to your changelist
table.

3 usable base classes are provided:
  - CSVExportableAdmin which adds comma-separated export to your changelist
  - PipeExportableAdmin which adds pipe-separated export to your changelist
  - MultiExportableAdmin which adds comma- and pipe-separated export to your
    changelist

If you wish to use a different delimeter, you can simply use the ExportableAdmin
base class and set the ``export_formats`` attribte to contain the formats you
desire. This should be an iterable of 2-tuples, each containing:::
    (format-name, delimiter) -- ex: (u'CSV', u',')

By default, up to 10,000 rows will be exported, though this can be changed
easily by setting the ``export_queryset_limit`` attribute on your ModelAdmin.

Django > 1.3 is required, at which point the standard changelist_view() returns
a TemplateResponse. This allows us to change the template used after the
response is created, so that we can output CSV instead of the standard HTML
view.  Django <= 1.3 requires an alternate version of this app in which the
changelist_view code is duplicated and modified slightly to change the template
and setup the response for download instead of display.

Django > 1.3: https://github.com/jwineinger/django-exportable-admin  
Django <= 1.3: https://github.com/jwineinger/django-exportable-admin/tree/pre-tr

Note: if you alter ``change_list_template`` on your ModelAdmin subclass, the
"Export ..." button(s) will not appear. You will need to add them manually to your
template or link to the correct url(s) by some other means.

Examples
--------

Simple example:
~~~~~~~~~~~~~~~

::

    # myapp/admin.py
    from django.contrib import admin
    from django_exportable_admin.admin import CSVExportableAdmin
    from models import MyModel

    class MyAdmin(CSVExportableAdmin):
        list_display = ('name','number','decimal','url','calc')

        def url(self, obj):
            return obj.filefield.url

        def calc(self, obj):
            return obj.number * obj.decimal

    admin.site.register(MyModel, MyAdmin)

.. image :: https://github.com/jwineinger/django-exportable-admin/raw/master/button-demo.png

Complex example:
~~~~~~~~~~~~~~~~

::

    # myapp/admin.py
    from django.contrib import admin
    from django_exportable_admin.admin import ExportableAdmin
    from models import MyModel

    class MyModelAdmin(ExportableAdmin):
        list_display = ('field1','field2','calculated_field')

        # only output 100 rows max
        export_queryset_limit = 100

        # setup tab and semicolon export formats
        export_formats = (
            (u'Tab', u'\t'),
            (u'Semicolon', u';'),
        )

        def calculated_field(self, obj):
            return u"%.3f" % obj.float_field / 33.7
        calculated_field.short_description = 'Arbitrary Title'
    admin.site.register(MyModel, MyModelAdmin)
