#!/usr/bin/env python
from setuptools import find_packages, setup

project = "sklearn-hierarchical-classification"
version = "0.1.0"

setup(
    name=project,
    version=version,
    description="Hierarchical classification interface extensions for scikit-learn",
    author="Globality Engineering",
    author_email="engineering@globality.com",
    url="https://github.com/globality-corp/sklearn-hierarchical-classification",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "networkx",
        "scikit-learn",
        "unidecode>=0.4.21",
        "six>=1.10.0",
    ],
    setup_requires=[
        "nose>=1.3.7",
    ],
    tests_require=[
        "coverage>=3.7.1",
        "mock>=2.0.0",
        "PyHamcrest>=1.9.0",
    ],
)
