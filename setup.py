#!/usr/bin/env python

from setuptools import setup

setup(name='sciex',
      packages=['sciex'],
      version='0.2',
      description='Framework for "scientific" experiments (Result organization; Experiment and Trial setup; Baseline Comparisons)',
      python_requires='>3.6',
      install_requires=[
          'pyyaml',
          'numpy',
      ],
      author='Kaiyu Zheng',
      author_email='kaiyutony@gmail.com'
)
