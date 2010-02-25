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
"""Custom errors for SPAM.

SPAM errors are derived from ``HTTPClientError`` and are given a 400 HTTP error
code, so the WSGI error middleware can take care of them."""

from tg.exceptions import HTTPClientError

class SPAMError(HTTPClientError):
    """SPAM Error."""
    code = 400
    title = 'SPAM Error'
    explanation = ''


class SPAMDBError(SPAMError):
    """Database Error."""
    code = 400
    title = 'Database Error'
    explanation = ''


class SPAMDBNotFound(SPAMError):
    """DB Element Not Found."""
    code = 400
    title = 'DB Element Not Found'
    explanation = ''


class SPAMRepoError(SPAMError):
    """Repository Error."""
    code = 400
    title = 'Repository Error'
    explanation = ''


class SPAMRepoNotFound(SPAMError):
    """Repository Not Found."""
    code = 400
    title = 'Repository Not Found'
    explanation = ''


