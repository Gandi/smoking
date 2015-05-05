import os
import re
import sys

from setuptools import setup, find_packages

PY3 = sys.version_info[0] == 3
here = os.path.abspath(os.path.dirname(__file__))
name = 'smoking'

with open(os.path.join(here, 'README.rst')) as readme:
    README = readme.read()
with open(os.path.join(here, 'CHANGES.rst')) as changes:
    CHANGES = changes.read()

with open(os.path.join(here, name, '__init__.py')) as v_file:
    version = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(v_file.read()).group(1)


requires = ['requests', 'lxml', 'nose', 'needle']


setup(name=name,
      version=version,
      description='Test your sitemap',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
      ],
      author='Gandi',
      author_email='feedback@gandi.net',
      url='https://github.com/Gandi/{name}'.format(name=name),
      keywords='web pyramid pylons',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      )
