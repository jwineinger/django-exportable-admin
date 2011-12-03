import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "django-exportable-admin",
    version = "2.1",

    packages = find_packages(),

    author = "Jay Wineinger",
    author_email = "jay.wineinger@gmail.com",

    description = "An app to allow Django admin changelists to be exported to CSV",
    long_description=open('README.rst').read(),

    url = "https://github.com/jwineinger/django-exportable-admin",
    download_url = "https://github.com/jwineinger/django-exportable-admin/downloads",

    install_requires = [
        "Django >= 1.4"
    ],

    include_package_data = True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)
