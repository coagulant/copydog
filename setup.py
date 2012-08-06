from distutils.core import setup
from copydog import __version__


setup(
    name='copydog',
    version=__version__,
    packages=['copydog', 'copydog.api', 'copydog.utils'],
    install_requires=[
        'requests==0.13.6',
        'redis==2.6',
        'pytz==2012c',
        'docopt==0.4.1',
        'PyYAML==3.10',
        'python-daemon==1.5.5',
    ],
    tests_require=[
        'nose==1.1.2',
        'mock==1.0b1',
        'sphinx==1.1.3',
        'texttable==0.8.1',
        'tox==1.4.2',
    ],
    url='https://github.com/coagluant/copydog',
    license='MIT',
    author='coagulant',
    author_email='baryshev@gmail.com',
    description='Copies issues between Redmine and Trello on the fly',
    long_description=open('README.rst').read(),
    classifiers=[
        'Development Status :: 3 - Alpha',
    ]
)
