# coding: utf-8

"""
    Segment Analyser
"""

from setuptools import setup, find_packages  # noqa: H301

NAME = "segment-analyzer"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["black", "pre-commit", "flask"]

setup(
    name=NAME,
    version=VERSION,
    description="Segment Analyzer",
    author_email="",
    url="",
    keywords=["Segment", "Analyze"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    Segment Analyzer
    """,
)
