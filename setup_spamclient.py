# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='spamclient',
    version='0.2',
    description='a standalone client for SPAM',
    author='Lorenzo Pierfederici',
    author_email='lpierfederici@gmail.com',
    #url='',
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    package_data={'spam': ['i18n/*/LC_MESSAGES/*.mo']},
    message_extractors={'spam': [
            ('**.py', 'python', None)]},
)
