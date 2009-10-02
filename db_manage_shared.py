#!/usr/bin/env python
from migrate.versioning.shell import main

main(url='sqlite:///shared.sqlite',repository='db_versioning_shared/')
