import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = "django_inlines",
    version = "0.7",
    url = 'http://github.com/mintchaos/django_inlines',
    license = 'BSD',
    description = "For embedding anything you'd like into text in your django apps.",
    long_description = read('README.rst'),
    
    author = 'Christian Metts',
    author_email = 'xian@mintchaos.com',
    packages = ['django_inlines'],
    install_requires = ['setuptools'],
    
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
    
)
