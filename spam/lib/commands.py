import sys, os
from paste.script import command
from sphinx.application import Sphinx

class BuildDocs(command.Command):

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

