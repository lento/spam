# -*- coding: utf-8 -*-
"""Setup the SPAM application"""

import logging
import transaction
from tg import config

def setup_schema(command, conf, vars):
    """Place any commands to setup SPAM here"""
    # Load the models

    # <websetup.websetup.schema.before.model.import>
    from spam import model
    # <websetup.websetup.schema.after.model.import>

    
    # <websetup.websetup.schema.before.metadata.create_all>
    print "Creating tables"
    model.versioning.db_init('spam')
    model.versioning.db_upgrade('spam')
    # <websetup.websetup.schema.after.metadata.create_all>
    transaction.commit()
