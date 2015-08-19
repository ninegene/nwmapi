import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.md')) as f:
    CHANGES = f.read()

requires = [
    'Cython',
    'falcon',
    'SQLAlchemy',
    'waitress',
]

setup(name='nwmapi',
      version='0.0',
      description='nwmapi',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Falcon",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Aung Lwin Oo',
      author_email='aungloo@gmail.com',
      url='',
      keywords='web api falcon',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='nwmapi',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = nwmapi:main
      [console_scripts]
      initialize_nwmdb = nwmapi.scripts.initializedb:main
      """,
      )
