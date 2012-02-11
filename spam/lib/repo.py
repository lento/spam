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
"""Mercurial repository management."""

import os, shutil, tempfile, zipfile, glob, time
from mercurial import ui, hg, commands, match
from mercurial.error import RepoError
from tg import app_globals as G
from spam.lib.exceptions import SPAMRepoError, SPAMRepoNotFound
from spam.model import session_get, libgroup_get

import logging
log = logging.getLogger(__name__)

repo_ui = ui.ui()
repo_ui.setconfig('ui', 'interactive', 'False')

# Repository
def repo_get(proj):
    """Return the mercurial repository for ``proj``."""
    repo_path = os.path.join(G.REPOSITORY, proj)
    try:
        return hg.repository(repo_ui, repo_path)
    except RepoError:
        raise SPAMRepoNotFound('"%s" is not a valid HG repository' % repo_path)

def repo_init(proj):
    """Init a new mercurial repository for ``proj``."""
    repo_path = os.path.join(G.REPOSITORY, proj)
    try:
        repo = repo_get(proj)
    except SPAMRepoNotFound:
        commands.init(repo_ui, repo_path)
        repo = repo_get(proj)
    
    hgignore_path = os.path.join(G.REPOSITORY, proj, '.hgignore')
    if not os.path.exists(hgignore_path):
        hgignore = open(hgignore_path, 'w')
        hgignore.write('syntax: regexp\n')
        hgignore.write('^.previews/')
        hgignore.close()
    
    if not '.hgignore' in repo['tip']:
        commands.add(repo_ui, repo, hgignore_path)
        matched = match.exact(repo.root, repo.getcwd(), ['.hgignore'])
        commit_id = repo.commit('add .hgignore', user='system', match=matched)

# Commit
def commit_single(proj, asset, filename, text, username=None):
    """Commit a single file to the repository and returns the revision id."""
    repo_path = os.path.join(G.REPOSITORY, proj)
    repo = repo_get(proj)
    
    if isinstance(filename, list):
        raise SPAMRepoError('expected a single file for asset %s' % asset.id)

    text = 'asset %s - %s' % (asset.id, text)
    encodedtext = text.encode('utf-8')
    targets = []
    
    uploadedfile = os.path.join(G.UPLOAD, filename)
    target_path = asset.path.encode()
    target_repo_path = os.path.join(repo_path, target_path)
    if not os.path.exists(os.path.dirname(target_repo_path)):
        os.makedirs(os.path.dirname(target_repo_path))
    shutil.move(uploadedfile, target_repo_path)
    
    if not target_path in repo['tip']:
        commands.add(repo_ui, repo, target_repo_path)

    targets.append(target_path)
    
    matched = match.exact(repo.root, repo.getcwd(), targets)
    commit_id = repo.commit(encodedtext, user=username, match=matched)
    if commit_id:
        return repo[commit_id].hex()
    else:
        return None

def commit_multi(proj, asset, filenames, text, username=None):
    """Commit multiple files to the repository and returns the revision id."""
    repo_path = os.path.join(G.REPOSITORY, proj)
    repo = repo_get(proj)
    
    if not isinstance(filenames, list):
        raise SPAMRepoError('expected a list of files for asset %s' % asset.id)

    text = 'asset %s - %s' % (asset.id, text)
    encodedtext = text.encode('utf-8')
    target_sequence_path = asset.path.replace('#', '%04d')
    targets = []
    
    for i, filename in enumerate(filenames):
        n = i + 1
        uploadedfile = os.path.join(G.UPLOAD, filename)
        target_path = (target_sequence_path % n).encode()
        target_repo_path = os.path.join(repo_path, target_path)
        if not os.path.exists(os.path.dirname(target_repo_path)):
            os.makedirs(os.path.dirname(target_repo_path))
        shutil.move(uploadedfile, target_repo_path)
        
        if not target_path in repo['tip']:
            commands.add(repo_ui, repo, target_repo_path)
    
        targets.append(target_path)
        
    matched = match.exact(repo.root, repo.getcwd(), targets)
    commit_id = repo.commit(encodedtext, user=username, match=matched)
    if commit_id:
        return repo[commit_id].hex()
    else:
        return None

def commit(proj, asset, filenames, text, username=None):
    """Helper to commit a new version of an asset to the repository.
    
    Call :meth:``commit_multi`` or :meth:``commit_single`` based on the asset type."""
    if asset.is_sequence:
        return commit_multi(proj, asset, filenames, text, username=None)
    else:
        return commit_single(proj, asset, filenames[0], text, username=None)

# Cat
def cat_single(proj, assetver):
    """Return the file corresponding to the given asset version, retriving it
    from the mercurial repository."""
    repo_path = os.path.join(G.REPOSITORY, proj)
    repo = repo_get(proj)
    
    target_file_name = os.path.join(repo_path, assetver.asset.path)
    temp = tempfile.NamedTemporaryFile()
    commands.cat(repo_ui, repo, target_file_name, output=temp.name,
                                                            rev=assetver.repoid)
    return temp

def cat_multi(proj, assetver):
    """Return the files corresponding to the given asset version in a zip
    archive (ready for http download), retriving them from the mercurial
    repository."""
    if not assetver.asset.is_sequence:
        raise SPAMRepoError('asset %s is not a sequence of files' %
                                                            assetver.asset.id)
    
    repo_path = os.path.join(G.REPOSITORY, proj)
    repo = repo_get(proj)
    
    target_path = assetver.asset.path.replace('#', '*').encode()
    target_filename = os.path.join(repo_path, target_path).encode()
    targets = glob.glob(target_filename)

    ztemp = tempfile.NamedTemporaryFile()
    zfile = zipfile.ZipFile(ztemp.name, 'w')
    for target in targets:
        temp = tempfile.NamedTemporaryFile()
        commands.cat(repo_ui, repo, target, output=temp.name,
                                                            rev=assetver.repoid)
        name = os.path.basename(target)
        name, ext = os.path.splitext(name)
        name, frame = os.path.splitext(name)
        name = name.rstrip('.#')
        verdir = '%s_v%03d' % (name, assetver.ver)
        vername = '%s_v%03d%s%s' % (name, assetver.ver, frame, ext)
        zfile.write(temp.name, os.path.join(verdir, vername))
        temp.close()
    zfile.close()
    return ztemp

def cat(proj, assetver):
    """Helper to retrive the file(s) corresponding to a specific asset version
    from the repository.
    
    Call :meth:``cat_multi`` or :meth:``cat_single`` based on the asset type."""
    if assetver.asset.is_sequence:
        return cat_multi(proj, assetver)
    else:
        return cat_single(proj, assetver)

# Directories
def project_create_dirs(proj):
    """Create default directories in the repository for ``proj``."""
    repo_path = os.path.join(G.REPOSITORY, proj)
    try:
        os.makedirs(repo_path)
        for d in G.DEFAULT_PROJ_DIRS:
            os.makedirs(os.path.join(repo_path, d))
    except OSError, error:
        # error 17 is "file exists", in that case we just skip the exception
        if not error.errno==17:
            raise SPAMRepoError("Couldn't create directories for project %s" %
                                                                        path)

def scene_create_dirs(proj, scene):
    """Create directories in the repository for ``scene``."""
    path = os.path.join(G.REPOSITORY, proj, scene.path)
    previews_path = os.path.join(G.REPOSITORY, proj, G.PREVIEWS, scene.path)
    try:
        os.makedirs(path)
        os.makedirs(previews_path)
    except OSError, error:
        # error 17 is "file exists", in that case we just skip the exception
        if not error.errno==17:
            raise SPAMRepoError("Couldn't create directories for scene %s" %
                                                                        path)

def shot_create_dirs(proj, shot):
    """Create directories in the repository for ``shot``."""
    path = os.path.join(G.REPOSITORY, proj, shot.path)
    previews_path = os.path.join(G.REPOSITORY, proj, G.PREVIEWS, shot.path)
    try:
        os.makedirs(path)
        os.makedirs(previews_path)
    except OSError, error:
        # error 17 is "file exists", in that case we just skip the exception
        if not error.errno==17:
            raise SPAMRepoError("Couldn't create directories for shot %s" %
                                                                        path)

def libgroup_create_dirs(proj, libgroup):
    """Create directories in the repository for ``libgroup``."""
    path = os.path.join(G.REPOSITORY, proj, libgroup.path)
    previews_path = os.path.join(G.REPOSITORY, proj, G.PREVIEWS, libgroup.path)
    try:
        os.makedirs(path)
        os.makedirs(previews_path)
    except OSError, error:
        # error 17 is "file exists", in that case we just skip the exception
        if not error.errno==17:
            raise SPAMRepoError("Couldn't create directories for libgroup %s" %
                                                                        path)


