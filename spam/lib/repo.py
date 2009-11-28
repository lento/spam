import re, os
from mercurial import ui, hg, commands, match
from mercurial.error import RepoError
from tg import config
from spam.lib.exceptions import SPAMRepoNotFound
from spam.model import session_get, Scene

REPOSITORY = config.get('repository', '/var/lib/spam/repo')
PREVIEWS = config.get('previews_dir', '.previews')
SCENES = config.get('default_scenes_dir', 'scenes')
LIBRARY = config.get('default_library_dir', 'library')
ADDITIONAL_PROJ_DIRS = config.get('additional_proj_dirs', '').split()
DEFAULT_PROJ_DIRS = [SCENES, LIBRARY, PREVIEWS] + ADDITIONAL_PROJ_DIRS

pattern_name = re.compile('^[a-zA-Z0-9_\-]+$')

repo_ui = ui.ui()
repo_ui.setconfig('ui', 'interactive', 'False')

# Repository
def repo_get(proj):
    repo_path = os.path.join(REPOSITORY, proj)
    try:
        return hg.repository(repo_ui, repo_path)
    except RepoError:
        raise SPAMRepoNotFound('"%s" is not a valid HG repository' % repo_path)

def repo_init(proj):
    repo_path = os.path.join(REPOSITORY, proj)
    try:
        repo = repo_get(proj)
    except SPAMRepoNotFound:
        commands.init(repo_ui, repo_path)
        repo = repo_get(proj)
    
    hgignore_path = os.path.join(REPOSITORY, proj, '.hgignore')
    if not os.path.exists(hgignore_path):
        hgignore = open(hgignore_path, 'w')
        hgignore.write('syntax: regexp\n')
        hgignore.write('^.previews/')
        hgignore.close()
    
    if not '.hgignore' in repo['tip']:
        repo.add(['.hgignore'])
        matched = match.exact(repo.root, repo.getcwd(), ['.hgignore'])
        commitid = repo.commit('add .hgignore', user='system', match=matched)

# Directories
def project_create_dirs(proj):
    repo_path = os.path.join(REPOSITORY, proj)
    try:
        os.makedirs(repo_path)
        for d in DEFAULT_PROJ_DIRS:
            os.makedirs(os.path.join(repo_path, d))
    except (OSError):
        pass


