from distutils.core import setup
from copydog import __version__


setup(
    name='copydog',
    version=__version__,
    packages=['copydog', 'copydog.api', 'copydog.utils'],
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
