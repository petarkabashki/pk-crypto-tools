from setuptools import setup, Extension
import numpy

module = Extension('positions',
                   sources=['positions.c'],
                   include_dirs=[numpy.get_include()])

setup(name='positions',
      version='1.0',
      description='A Python module to calculate positions for trading strategies',
      ext_modules=[module])
