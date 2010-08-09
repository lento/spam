# -*- coding: utf-8 -*-
#
# This file is part of SPAM (Spark Project & Asset Manager).
#
# SPAM is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPAM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPAM.  If not, see <http://www.gnu.org/licenses/>.
#
# Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
# Contributor(s): 
#
"""Setup the SPAM database data"""

from tg import config
from spam import model

import transaction

import logging
log = logging.getLogger(__name__)

def bootstrap(command, conf, vars):
    """Commands for the first-time setup of SPAM database data."""

    session = model.session_get()
    # auth
    from sqlalchemy.exc import IntegrityError
    try:
        admin = model.User(u'admin', display_name=u'SPAM Administrator')
        admin.password = u'none'

        session.add(admin)

        administrators = model.Group(u'administrators',
                                            display_name=u'SPAM Administrators')

        administrators.users.append(admin)

        session.add(administrators)
        
        session.flush()
        transaction.commit()
    except IntegrityError:
        log.info('Warning, there was a problem adding your auth data, it may '
                                                    'have already been added:')
        import traceback
        log.info(traceback.format_exc())
        transaction.abort()
        log.info('Continuing with bootstrapping...')
        

    # migrate versioning
    try:
        migrate = model.Migrate(repository_id=u'SPAM DB versions repository',
                                    repository_path=u'db_versioning', version=3)
        session.add(migrate)
        session.flush()
        transaction.commit()
    except IntegrityError:
        log.info('Warning, there was a problem adding migrate versioning data,'
                                            ' it may have already been added:')
        import traceback
        log.info(traceback.format_exc())
        transaction.abort()
        log.info('Continuing with bootstrapping...')

    # default categories
    try:
        design = model.Category(u'design', ordering=1,
                        naming_convention=u'^[a-zA-Z0-9_]+_DRW\.[a-zA-Z0-9]+$')
        session.add(design)
        
        modelling = model.Category(u'model', ordering=2,
                        naming_convention=u'^[a-zA-Z0-9_]+_MDL\.[a-zA-Z0-9]+$')
        session.add(modelling)
        
        texture = model.Category(u'texture', ordering=3,
                        naming_convention=u'^[a-zA-Z0-9_]+_TEX\.[a-zA-Z0-9]+$')
        session.add(texture)
        
        rig = model.Category(u'rig', ordering=4,
                        naming_convention=u'^[a-zA-Z0-9_]+_RIG\.[a-zA-Z0-9]+$')
        session.add(rig)
        
        storyboard = model.Category(u'storyboard', ordering=5,
                        naming_convention=u'^[a-zA-Z0-9_]+_STB\.#\.[a-zA-Z0-9]+$')
        session.add(storyboard)

        plate = model.Category(u'plate', ordering=6,
                        naming_convention=u'^[a-zA-Z0-9_]+_PLT\.#\.[a-zA-Z0-9]+$')
        session.add(plate)

        paint = model.Category(u'paint', ordering=7,
                        naming_convention=u'^[a-zA-Z0-9_]+_PNT\.[a-zA-Z0-9]+$')
        session.add(paint)

        audio = model.Category(u'audio', ordering=8,
                        naming_convention=u'^[a-zA-Z0-9_]+_AUD\.[a-zA-Z0-9]+$')
        session.add(audio)

        animatic = model.Category(u'animatic', ordering=9,
                        naming_convention=u'^[a-zA-Z0-9_]+_A[23]D\.[a-zA-Z0-9]+$')
        session.add(animatic)

        layout = model.Category(u'layout', ordering=10,
                        naming_convention=u'^[a-zA-Z0-9_]+_LAY\.[a-zA-Z0-9]+$')
        session.add(layout)

        animation = model.Category(u'animation', ordering=11,
                        naming_convention=u'^[a-zA-Z0-9_]+_ANI\.[a-zA-Z0-9]+$')
        session.add(animation)

        effects = model.Category(u'effects', ordering=12,
                        naming_convention=u'^[a-zA-Z0-9_]+_FX\.[a-zA-Z0-9]+$')
        session.add(effects)

        render = model.Category(u'render', ordering=13,
                        naming_convention=u'^[a-zA-Z0-9_]+_RND\.#\.[a-zA-Z0-9]+$')
        session.add(render)

        compositing = model.Category(u'compositing', ordering=14,
                        naming_convention=u'^[a-zA-Z0-9_]+_CMP\.#\.[a-zA-Z0-9]+$')
        session.add(compositing)

        transaction.commit()
    except IntegrityError:
        log.info('Warning, there was a problem adding default categories '
                                            'they may have already been added:')
        import traceback
        log.info(traceback.format_exc())
        transaction.abort()
        log.info('Continuing with bootstrapping...')

