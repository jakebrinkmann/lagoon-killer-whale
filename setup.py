from setuptools import setup

def version():
    with open('version.txt') as f:
        return f.read()

def readme():
    with open('README.md') as f:
        return f.read()


setup(name='espa-web',
      version=version(),
      description='Graphical User Interface (GUI) for the ESPA-API',
      long_description=readme(),
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: Public Domain',
        'Programming Language :: Python :: 3.6',
      ],
      keywords='usgs eros lsrd espa',
      url='http://github.com/usgs-eros/espa-web',
      author='USGS EROS ESPA',
      author_email='',
      license='Unlicense',
      packages=None,
      install_requires=[
          'python-memcached',
          'requests',
          'simplejson',
          'uWSGI',
          'python-dateutil',
      ],
      # List additional groups of dependencies here (e.g. development
      # dependencies). You can install these using the following syntax,
      # for example:
      # $ pip install -e .[test]
      extras_require={
          'test': [
              'pytest',
              'pytest-cov',
              'vcrpy',
              'hypothesis',
                  ],
          'doc': [
              'sphinx',
              'sphinx-autobuild',
              'sphinx_rtd_theme'],
          'dev': [],
      },
      entry_points={
          'console_scripts': [
          ],
      },
      include_package_data=True,
      zip_safe=False
)
