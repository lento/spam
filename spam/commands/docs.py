# -*- coding: utf-8 -*-
#
# SPAM Spark Project & Asset Manager
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this program; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
#
# Original Copyright (c) 2010, Lorenzo Pierfederici <lpierfederici@gmail.com>
# Contributor(s): 
#
"""build-docs paster command."""

import sys, os
from paste.script import command
from sphinx.application import Sphinx

class BuildDocs(command.Command):
    """Paster command to build SPAM documentation from sphinx sources."""
    max_args = 0
    min_args = 0

    usage = ""
    summary = "Build SPAM documentation"
    group_name = "SPAM"

    parser = command.Command.standard_parser(verbose=True)
    #parser.add_option('--goodbye',
    #                  action='store_true',
    #                  dest='goodbye',
    #                  help="Say 'Goodbye' instead")

    def command(self):
        srcdir = os.path.abspath('docs/source')
        confdir = os.path.abspath('docs/source')
        outdir = os.path.abspath('docs/build')
        doctreedir = os.path.abspath('docs/build/.doctrees')
        buildername = 'html'
        status = sys.stdout
        confoverrides = {}
        htmlcontext = {}
        confoverrides['html_context'] = htmlcontext
        all_files = False
        filenames = None

        app = Sphinx(srcdir, confdir, outdir, doctreedir, buildername,
                                                        confoverrides, status)
        app.build(all_files, filenames)
        return app.statuscode

