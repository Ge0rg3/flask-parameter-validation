"""
Flask-Parameter-Validation
-------------

Get and validate all Flask input parameters with ease.
"""

from setuptools import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="Flask-Parameter-Validation",
    version="2.4.0",
    url="https://github.com/Ge0rg3/flask-parameter-validation",
    license="MIT",
    author="George Omnet",
    author_email="flaskparametervalidation@georgeom.net",
    description="Get and validate all Flask input parameters with ease.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["flask_parameter_validation", "flask_parameter_validation.exceptions", "flask_parameter_validation.parameter_types"],
    zip_safe=False,
    package_data={"": ["templates/fpv_default_docs.html"]},
    include_package_data=True,
    platforms="any",
    install_requires=[
        "Flask",
        "flask[async]",
        "python-dateutil",
        "jsonschema",
    ],
    python_requires=">=3.9,<3.14",
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Development Status :: 5 - Production/Stable",
        "Framework :: Flask",
        "Topic :: Software Development :: Documentation",
        "Topic :: File Formats :: JSON :: JSON Schema",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
