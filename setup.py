"""Minimal setup file"""
import os
from setuptools import setup, find_packages


here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    readme_text = f.read()

setup(
    name='euchre',
    version='0.1.0',
    description='A Euchre game',
    long_description=readme_text,

    author='Colin Ong-Dean',
    author_email='',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    install_requires=[],
    extras_require={},

    # entry_points={
    #     'console_scripts': [
    #         'tasks = tasks.cli:tasks_cli',
    #     ]
    # },
)
