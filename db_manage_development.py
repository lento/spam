#!/usr/bin/env python
from migrate.versioning.shell import main
main(url='sqlite:////var/tmp/spam/db/spam.sqlite', debug='False', repository='db_versioning/')
