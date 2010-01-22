from paste.script import command
from mrapps.mrclientmaker import ClientMaker
from spam.commands import pylonsenv
pylonsenv.setup()

from spam.controllers import category, tag as _tag, note as _note, project
from spam.controllers import scene, shot, libgroup, asset

def build_client(filename):
    cat = category.Controller()
    tag = _tag.Controller()
    note = _note.Controller()
    proj = project.Controller()
    sc = scene.Controller()
    sh = shot.Controller()
    lib = libgroup.Controller()
    ast = asset.Controller()

    maker = ClientMaker('SPAM')

    # Category
    group = 'category'
    maker.add_call(cat.get_one, group, 'get', group, 'category')
    maker.add_call(cat.post, group, 'new', group)
    maker.add_call(cat.put, group, 'edit', group, _method='PUT')
    maker.add_call(cat.post_delete, group, 'delete', group, _method='DELETE')

    # Tag
    group = 'tag'
    maker.add_call(tag.get_one, group, 'get', group, 'tag')
    maker.add_call(tag.post, group, 'new', group)
    maker.add_call(tag.post_delete, group, 'delete', group, _method='DELETE')
    maker.add_call(tag.post_remove, group, 'remove', group, _method='REMOVE')

    # Note
    group = 'note'
    maker.add_call(note.get_one, group, 'get', group, 'note')
    maker.add_call(note.post, group, 'new', group)
    maker.add_call(note.post_delete, group, 'delete', group, _method='DELETE')
    maker.add_call(note.pin, group, 'pin', group, _method='PIN')
    maker.add_call(note.unpin, group, 'unpin', group, _method='UNPIN')

    # Project
    group = 'project'
    maker.add_call(proj.get_one, group, 'get', group, 'project')
    maker.add_call(proj.post, group, 'new', group)
    maker.add_call(proj.put, group, 'edit', group, _method='PUT')
    maker.add_call(proj.post_delete, group, 'delete', group, _method='DELETE')
    maker.add_call(proj.post_archive, group, 'archive', group, _method='ARCHIVE')
    maker.add_call(proj.post_activate, group, 'activate', group, _method='ACTIVATE')

    # Scene
    group = 'scene'
    maker.add_call(sc.get_one, group, 'get', group, 'scene')
    maker.add_call(sc.post, group, 'new', group)
    maker.add_call(sc.put, group, 'edit', group, _method='PUT')
    maker.add_call(sc.post_delete, group, 'delete', group, _method='DELETE')

    # Shot
    group = 'shot'
    maker.add_call(sh.get_one, group, 'get', group, 'shot')
    maker.add_call(sh.post, group, 'new', group)
    maker.add_call(sh.put, group, 'edit', group, _method='PUT')
    maker.add_call(sh.post_delete, group, 'delete', group, _method='DELETE')

    # Libgroup
    group = 'libgroup'
    maker.add_call(lib.get_one, group, 'get', group, 'libgroup')
    maker.add_call(lib.post, group, 'new', group)
    maker.add_call(lib.put, group, 'edit', group, _method='PUT')
    maker.add_call(lib.post_delete, group, 'delete', group, _method='DELETE')

    # Asset
    group = 'asset'
    maker.add_call(ast.get_one, group, 'get', group, 'asset')
    maker.add_call(ast.post, group, 'new', group)
    maker.add_call(ast.post_delete, group, 'delete', group, _method='DELETE')
    maker.add_call(ast.checkout, group, 'checkout', group, _method='CHECKOUT')
    maker.add_call(ast.release, group, 'release', group, _method='RELEASE')
    maker.add_call(ast.post_publish, group, 'publish', group, _method='PUBLISH')
    maker.add_call(ast.post_submit, group, 'submit', group, _method='SUBMIT')
    maker.add_call(ast.post_recall, group, 'recall', group, _method='RECALL')
    maker.add_call(ast.post_sendback, group, 'sendback', group, _method='SENDBACK')
    maker.add_call(ast.post_approve, group, 'approve', group, _method='APPROVE')
    maker.add_call(ast.post_revoke, group, 'revoke', group, _method='REVOKE')
    #maker.add_call(ast.download, group, 'download', group, _method='DOWNLOAD')

    output = open(filename, 'w+')
    output.write(maker.render())
    output.close()

class BuildClient(command.Command):

    max_args = 1
    min_args = 0

    usage = ""
    summary = "Build a standalone SPAM client"
    group_name = "SPAM"

    parser = command.Command.standard_parser(verbose=True)
    parser.add_option('--filename',
                      default='spam/spamclient.py',
                      help="save output in <filename>")

    def command(self):
        build_client(self.options.filename)
        print('Saved output in <%s>' % self.options.filename)
        return

