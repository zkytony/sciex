#!/usr/bin/env python

from setuptools import setup
from distutils.extension import Extension

setup(name='sciex',
      packages=['sciex'],
      version='0.0',
      description='Framework for "scientific" experiments (Result organization; Experiment and Trial setup; Baseline Comparisons)',
      python_requires='>3.6',
      install_requires=[
          'pyyaml',
          'numpy',
      ],
      author='Kaiyu Zheng',
      author_email='kaiyutony@gmail.com'
     )

