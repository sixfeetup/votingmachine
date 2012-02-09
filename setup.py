import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

requires = [
    'pyramid',
    'pyramid_zodbconn',
    'pyramid_tm',
    'ZODB3',
    'repoze.folder',
    'repoze.retry',
    'repoze.tm2',
    'repoze.zodbconn',
    'repoze.whoplugins.zodb',
    'deform',
    'nose',
    ]

setup(name='votingmachine',
      version='2.0.5',
      description='votingmachine',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires = requires,
      tests_require= requires,
      test_suite="votingmachine",
      entry_points = """\
      [paste.app_factory]
      main = votingmachine:main
      """,
      paster_plugins=['pyramid'],
      )
