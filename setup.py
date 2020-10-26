"""
Flask-Parameter-Validation
-------------

Get and validate all Flask input parameters with ease.
"""
from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='Flask-Parameter-Validation',
    version='1.0',
    url='https://github.com/Ge0rg3/',
    license='MIT',
    author='George Omnet',
    author_email='georgeomnet+flask-parameter-validation@gmail.com',
    description='Get and validate all Flask input parameters with ease.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    py_modules=['flask-parameter-validation'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
