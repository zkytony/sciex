# Copyright 2022 Kaiyu Zheng
# 
# Usage of this file is licensed under the MIT License.

#!/usr/bin/env python

from setuptools import setup

setup(name='sciex',
      packages=['sciex'],
      version='0.3',
      description='Framework for "scientific" experiments (Result organization; Experiment and Trial setup; Baseline Comparisons)',
      python_requires='>3.6',
      install_requires=[
          'pyyaml',
          'numpy',
      ],
      author='Kaiyu Zheng',
      author_email='kaiyutony@gmail.com'
)
