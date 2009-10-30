"""
Common data model.

This is where the model for projects is defined.
"""
from datetime import datetime

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import relation, synonym

from spam.model import DeclarativeBase, metadata, DBSession

__all__ = ['Project']


#{ Association tables


# Association table for the many-to-many relationship projects-users.
project_user_table = Table('__project_user', metadata,
    Column('project_id', Unicode(10), ForeignKey('projects.id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('user_id', Integer, ForeignKey('auth_users.user_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)

# Association table for the many-to-many relationship projects-admins.
project_admin_table = Table('__project_admin', metadata,
    Column('project_id', Unicode(10), ForeignKey('projects.id',
        onupdate="CASCADE", ondelete="CASCADE")),
    Column('user_id', Integer, ForeignKey('auth_users.user_id',
        onupdate="CASCADE", ondelete="CASCADE"))
)


#{ The Common model itself


class Project(DeclarativeBase):
    """
    Project definition.
    
    """
    
    __tablename__ = 'projects'
    
    #{ Columns
    id = Column(Unicode(10), primary_key=True)
    name = Column(Unicode(40))
    description = Column(Unicode)
    created = Column(DateTime, default=datetime.now)
    
    #{ Relations
    users = relation('User', secondary=project_user_table, backref='projects')
    admins = relation('User', secondary=project_admin_table,
                                                    backref='admin_projects')
    
    #{ Special methods
    def __init__(self, id, name=None, description=None):
        self.id = id
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Project: %s "%s">' % (self.id, self.name)
    
    #}



