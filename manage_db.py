#!/usr/bin/env python
from migrate.versioning.shell import main

main(url='sqlite:///spam.sqlite',repository='db_versioning/')
