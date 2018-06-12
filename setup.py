import os
from setuptools import setup, find_packages


def read(filename):
    '''Read a file and return the contents.'''
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='TurnTouch',
    version='0.3',
    url='https://github.com/antsar/python-turntouch',
    author='Anton Sarukhanov',
    author_email='code@ant.sr',
    description='Python library for the Turn Touch smart home remote',
    license='MIT',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        'bluepy==1.1.4',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Topic :: Home Automation',
    ]
)
