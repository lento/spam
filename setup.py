# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='spam',
    version='0.3.1',
    description='A project and asset manager for 3d animation and VFX productions',
    author='Lorenzo Pierfederici',
    author_email='lpierfederici@gmail.com',
    #url='',
    license='GPL v3',
    zip_safe=False,
    install_requires=[
        "TurboGears2 >= 2.1b2",
        "Babel >=0.9.4",
        "tw2.core",
        "tw2.forms",
        "tw2.dynforms",
        "tw2.livewidgets",
        "zope.sqlalchemy >= 0.4 ",
        "repoze.tm2 >= 1.0a4",
        "repoze.what-quickstart >= 1.0",
        "mercurial",
        "MySQL-python",
        "sqlalchemy-migrate",
                ],
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'spam'],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['WebTest', 'BeautifulSoup'],
    package_data={'spam': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    message_extractors={'spam': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('public/**', 'ignore', None)]},

    entry_points="""
    [paste.app_factory]
    main = spam.config.middleware:make_app

    [paste.app_install]
    main = pylons.util:PylonsInstaller

    [paste.paster_command]
    build-docs = spam.commands.docs:BuildDocs
    build-client = spam.commands.client:BuildClient
    """,
)
