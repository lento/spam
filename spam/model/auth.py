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
"""
Auth* related model.

This is where the models used by :mod:`repoze.who` and :mod:`repoze.what` are
defined.
"""
import os
from datetime import datetime
import sys
from hashlib import sha1

from tg import config
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import relation, synonym, backref
from spam.model import DeclarativeBase, metadata

__all__ = ['User', 'Group', 'Permission']


############################################################
# Association tables
############################################################

# This is the association table for the many-to-many relationship between
# groups and permissions. This is required by repoze.what.
groups_permissions_table = Table('__groups_permissions', metadata,
    Column('group_id', Integer, ForeignKey('groups.group_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('permission_id', Integer, ForeignKey('permissions.permission_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

# This is the association table for the many-to-many relationship between
# groups and members - this is, the memberships. It's required by repoze.what.
users_groups_table = Table('__users_groups', metadata,
    Column('user_id', Integer, ForeignKey('users.user_id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('group_id', Integer, ForeignKey('groups.group_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)


############################################################
# Auth
############################################################

class Group(DeclarativeBase):
    """
    Group definition for :mod:`repoze.what`.
    
    Only the ``group_name`` column is required by :mod:`repoze.what`.
    """
    __tablename__ = 'groups'
    
    # Columns
    group_id = Column(Unicode(40), primary_key=True)
    group_name = Column(Unicode(16), unique=True, nullable=False)
    display_name = Column(Unicode(255))
    created = Column(DateTime, default=datetime.now)
    
    # Relations
    users = relation('User', secondary=users_groups_table,
                                        backref=backref('groups', lazy=False))
    
    # Special methods
    def __init__(self, group_name, display_name):
        domain = config.auth_domain
        self.group_id = '%s-%s' % (domain, group_name)
        self.group_name = group_name
        self.display_name = display_name
    
    def __repr__(self):
        return '<Group: %s (%s)>' % (self.group_id, self.display_name)


class User(DeclarativeBase):
    """
    User definition.
    
    This is the user definition used by :mod:`repoze.who`, which requires at
    least the ``user_name`` column.
    """
    __tablename__ = 'users'
    
    # Columns
    user_id = Column(Unicode(40), primary_key=True)
    user_name = Column(Unicode(16), nullable=False)
    email_address = Column(Unicode(255), unique=True)
    display_name = Column(Unicode(255))
    _password = Column(Unicode(80))
    created = Column(DateTime, default=datetime.now)
    
    # Properties
    @property
    def permissions(self):
        """Return a set of strings for the permissions granted."""
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms

    def _set_password(self, password):
        """Hash ``password`` on the fly and store its hashed version."""
        hashed_password = password
        
        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password

        salt = sha1()
        salt.update(os.urandom(60))
        hash = sha1()
        hash.update(password_8bit + salt.hexdigest())
        hashed_password = salt.hexdigest() + hash.hexdigest()

        # Make sure the hashed password is an UTF-8 object at the end of the
        # process because SQLAlchemy _wants_ a unicode object for Unicode
        # columns
        if not isinstance(hashed_password, unicode):
            hashed_password = hashed_password.decode('UTF-8')

        self._password = hashed_password

    def _get_password(self):
        """Return the hashed version of the password."""
        return self._password

    password = synonym('_password', descriptor=property(_get_password,
                                                        _set_password))
    
    def validate_password(self, password):
        """
        Check the password against existing credentials.
        
        :param password: the password that was provided by the user to
            try and authenticate. This is the clear text version that we will
            need to match against the hashed one in the database.
        :type password: unicode object.
        :return: Whether the password is valid.
        :rtype: bool
        """
        hashed_pass = sha1()
        hashed_pass.update(password + self.password[:40])
        return self.password[40:] == hashed_pass.hexdigest()

    @property
    def projects_as_supervisor(self):
        return [s.project for s in self._supervisor_for]
    
    @property
    def projects_as_artist(self):
        return [a.project for a in self._artist_for]
    
    @property
    def projects(self):
        return (set(self.projects_as_supervisor) |
                set(self.projects_as_artist) |
                set(self.projects_as_admin))
    
    @property
    def id(self):
        return self.user_id
    
    @property
    def domain(self):
        return (self.user_id.split('-')[0])
    
    # Special methods
    def __init__(self, user_name, display_name=None, email=None):
        domain = config.auth_domain
        self.user_id = '%s-%s' % (domain, user_name)
        self.user_name = user_name
        self.display_name = display_name
        self.email_address = email
    
    def __repr__(self):
        return '<User %s (%s)>' % (self.user_id, self.display_name)

    def __json__(self):
        return dict(user_id=self.user_id,
                    id=self.id,
                    user_name=self.user_name,
                    display_name=self.display_name,
                    domain=self.domain,
                   )
    

class Permission(DeclarativeBase):
    """
    Permission definition for :mod:`repoze.what`.
    
    Only the ``permission_name`` column is required by :mod:`repoze.what`.
    """
    __tablename__ = 'permissions'
    
    # Columns
    permission_id = Column(Unicode(40), primary_key=True)
    permission_name = Column(Unicode(16), unique=True, nullable=False)
    description = Column(Unicode(255))
    
    # Relations
    groups = relation(Group, secondary=groups_permissions_table,
                                    backref=backref('permissions', lazy=False))
    
    # Special methods
    def __init__(self, permission_name, description):
        domain = config.auth_domain
        self.permission_id = '%s-%s' % (domain, permission_name)
        self.permission_name = permission_name
        self.description = description
    
    def __repr__(self):
        return '<Permission: %s (%s)>' % (self.permission_name,
                                                            self.description)

