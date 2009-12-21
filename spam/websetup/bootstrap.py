# -*- coding: utf-8 -*-
"""Setup the SPAM application"""

import logging
from tg import config
from spam import model

import transaction


def bootstrap(command, conf, vars):
    """Place any commands to setup SPAM here"""

    session = model.session_get()
    # <websetup.bootstrap.before.auth
    from sqlalchemy.exc import IntegrityError
    try:
        admin = model.User()
        admin.user_name = u'admin'
        admin.display_name = u'SPAM Administrator'
        admin._password = u'4e1b983227e6992278c9fc9346356e40169bef8839441bb9b9ddbb5174a3b89cdc27ad71d79245cd'

        session.add(admin)

        administrators = model.Group()
        administrators.group_name = u'administrators'
        administrators.display_name = u'SPAM Administrators'

        administrators.users.append(admin)

        session.add(administrators)
        
        session.flush()
        transaction.commit()
    except IntegrityError:
        print 'Warning, there was a problem adding your auth data, it may have already been added:'
        import traceback
        print traceback.format_exc()
        transaction.abort()
        print 'Continuing with bootstrapping...'
        

    # <websetup.bootstrap.after.auth>
    design = model.Category(u'design', ordering=1,
                    naming_convention=u'^[a-zA-Z0-9_]+_DRW\.[a-zA-Z0-9]+$')
    session.add(design)
    
    storyboard = model.Category(u'storyboard', ordering=2,
                    naming_convention=u'^[a-zA-Z0-9_]+_STB\.#\.[a-zA-Z0-9]+$')
    session.add(storyboard)

    animatic = model.Category(u'animatic', ordering=3,
                    naming_convention=u'^[a-zA-Z0-9_]+_A[23]D\.[a-zA-Z0-9]+$')
    session.add(animatic)

    layout = model.Category(u'layout', ordering=4,
                    naming_convention=u'^[a-zA-Z0-9_]+_LAY\.[a-zA-Z0-9]+$')
    session.add(layout)

    animation = model.Category(u'animation', ordering=5,
                    naming_convention=u'^[a-zA-Z0-9_]+_ANI\.[a-zA-Z0-9]+$')
    session.add(animation)

    transaction.commit()

