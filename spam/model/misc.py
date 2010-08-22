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
"""
Misc data model.

This is where the model for misc objects is defined.
"""
from datetime import datetime
from hashlib import sha1

from sqlalchemy import Table, ForeignKey, Column, UniqueConstraint, DDL
from sqlalchemy import ForeignKeyConstraint, and_, desc
from sqlalchemy.types import Unicode, UnicodeText, Integer, DateTime, Boolean
from sqlalchemy.types import String
from sqlalchemy.orm import relation, synonym, backref

from tg import config
from spam.model import DeclarativeBase, metadata
from spam.model.auth import User


############################################################
# Migrate versioning
############################################################
class Migrate(DeclarativeBase):
    __tablename__ = 'migrate_version'

    # Columns
    repository_id = Column(Unicode(250), primary_key=True)
    repository_path = Column(UnicodeText)
    version = Column(Integer)


############################################################
# Journal
############################################################
class Journal(DeclarativeBase):
    __tablename__ = 'journal'

    # Columns
    id = Column(String(40), primary_key=True)
    domain = Column(Unicode(24))
    user_id = Column(Unicode(40), ForeignKey('users.user_id'))
    text = Column(UnicodeText)
    created = Column(DateTime, default=datetime.now)

    # Relations
    user = relation('User', backref=backref('journal',
                                                    order_by=desc('created')))

    # Properties
    @property
    def strftime(self):
        return self.created.strftime('%Y.%m.%d-%H:%M')

    # Special methods
    def __init__(self, user, text):
        self.domain = config.auth_domain.decode('utf-8')
        self.user = user
        self.text = text
        self.created = datetime.now()
        hashable = '%s-%s-%s' % (self.created, self.user_id, self.text)
        self.id = sha1(hashable.encode('utf-8')).hexdigest()

    def __repr__(self):
        return '<Journal: (%s) %s: "%s">' % (self.created, self.user_id,
                                                                    self.text)

    def __json__(self):
        return dict(id=self.id,
                    domain=self.domain,
                    user_id=self.user_id,
                    text=self.text,
                    created=self.created,
                    strftime=self.strftime,
                   )

############################################################
# Tags
############################################################
# Association table for the many-to-many relationship taggables-tags.
taggables_tags_table = Table('__taggables_tags', metadata,
    Column('taggable_id', String(40), ForeignKey('taggables.id',
                                    onupdate='CASCADE', ondelete='CASCADE')),
    Column('tag_id', Unicode(40), ForeignKey('tags.id',
                                    onupdate='CASCADE', ondelete='CASCADE')),
)

class Taggable(DeclarativeBase):
    __tablename__ = 'taggables'

    # Columns
    id = Column(String(40), primary_key=True)
    association_type = Column(Unicode(50))

    # Properties
    @property
    def tagged(self):
        return getattr(self, 'tagged_%s' % self.association_type)

    # Methods
    def has_tags(self, tag_ids):
        find = set(tag_ids)
        tags = set([t.id for t in self.tags])
        return find.issubset(tags)

    # Special methods
    def __init__(self, id, association_type):
        self.id = id
        self.association_type = association_type

    def __repr__(self):
        return '<Taggable: %s (%s)>' % (self.id, self.association_type)


class Tag(DeclarativeBase):
    __tablename__ = 'tags'

    # Columns
    id = Column(Unicode(40), primary_key=True)

    # Relations
    taggables = relation(Taggable, secondary=taggables_tags_table,
                                backref=backref('tags', order_by='Tag.id'))

    # Properties
    @property
    def tagged(self):
        return [t.tagged for t in self.taggables]

    # Special methods
    def __init__(self, id):
        self.id = id

    def __repr__(self):
        return '<Tag: %s>' % self.id

    def __json__(self):
        return dict(id=self.id)


############################################################
# Notes
############################################################
class Annotable(DeclarativeBase):
    __tablename__ = 'annotables'

    # Columns
    id = Column(String(40), primary_key=True)
    association_type = Column(Unicode(50))

    # Properties
    @property
    def annotated(self):
        return getattr(self, 'annotated_%s' % self.association_type)

    # Special methods
    def __init__(self, id, association_type):
        self.id = id
        self.association_type = association_type

    def __repr__(self):
        return '<Annotable: %s (%s)>' % (self.id, self.association_type)


class Note(DeclarativeBase):
    __tablename__ = 'notes'

    # Columns
    id = Column(String(40), primary_key=True)
    annotable_id = Column(String(40), ForeignKey('annotables.id'))
    user_id = Column(Unicode(40), ForeignKey('users.user_id'))
    text = Column(UnicodeText)
    created = Column(DateTime, default=datetime.now)
    sticky = Column(Boolean, default=False)

    # Relations
    user = relation('User', backref=backref('notes',
                                    order_by=(desc('sticky'), desc('created'))))

    annotable = relation(Annotable, backref=backref('notes',
                                    order_by=(desc('sticky'), desc('created'))))

    # Properties
    @property
    def annotated(self):
        return self.annotable.annotated

    @property
    def strftime(self):
        return self.created.strftime('%d/%m/%Y %H:%M')

    @property
    def header(self):
        return '%s at %s' %(self.user.user_name, self.strftime)

    @property
    def summary(self):
        characters = 75
        summary = self.text[0:characters]
        if len(self.text) > characters:
            summary = '%s[...]' % summary
        return summary

    @property
    def lines(self):
        return [dict(line=l) for l in self.text.split('\n')]

    @property
    def project(self):
        return self.annotable.annotated.project

    @property
    def user_name(self):
        return self.user.user_name

    # Special methods
    def __init__(self, user, text):
        self.created = datetime.now()
        self.user = user
        self.text = text
        hashable = '%s-%s-%s' % (self.user_id, self.created, self.text)
        self.id = sha1(hashable.encode('utf-8')).hexdigest()

    def __repr__(self):
        return '<Note: by %s at %s "%s">' % (self.user.user_name,
                                                self.strftime,
                                                self.summary)

    def __json__(self):
        return dict(id=self.id,
                    project=self.project,
                    user=self.user,
                    user_name=self.user.user_name,
                    created=self.created,
                    text=self.text,
                    sticky=self.sticky,
                    strftime=self.strftime,
                    header=self.header,
                    summary=self.summary,
                    lines=self.lines,
                   )

