import os
from setuptools import setup, find_packages

version = __import__('django_exportable_admin').__version__


def read(fname):
    # read the contents of a text file
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="django-exportable-admin",
    version=version,
    url='https://github.com/sbussetti/django-exportable-admin',
    license='BSD',
    platforms=['OS Independent'],
    description="Provides a simple way to export Admin change-lists",
    long_description=read('README.rst'),
    author='Stefan Foulis, Steve Bussetti',
    author_email='stefan@foulis.ch',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=(
        "Django>=1.4.0a0",
    ),
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Topic :: Internet :: WWW/HTTP',
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
