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
"""JSON encoding functions using EAK-Rules.

Stolen from tg2.1 and modified to use standard lib json instead of simplejson.
"""

import datetime
import decimal

from json import JSONEncoder

import sqlalchemy

def is_saobject(obj):
    return hasattr(obj, '_sa_class_manager')

from sqlalchemy.engine.base import ResultProxy, RowProxy


# JSON Encoder class
class GenericJSON(JSONEncoder):
    """A JSON encoder that manages SQLAlchemy objects."""
    def default(self, obj):
        if hasattr(obj, '__json__') and callable(obj.__json__):
            return obj.__json__()
        elif isinstance(obj, (datetime.date, datetime.datetime)):
            return str(obj)
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif is_saobject(obj):
            props = {}
            for key in obj.__dict__:
                if not key.startswith('_sa_'):
                    props[key] = getattr(obj, key)
            return props
        elif isinstance(obj, ResultProxy):
            return list(obj)
        elif isinstance(obj, RowProxy):
            return dict(obj)
        else:
            return JSONEncoder.default(self, obj)

_instance = GenericJSON()


# General encoding functions
def encode(obj):
    """Return a JSON string representation of a Python object."""
    return _instance.encode(obj)

def encode_iter(obj):
    """Encode object, yielding each string representation as available."""
    return _instance.iterencode(obj)
