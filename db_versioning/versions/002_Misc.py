from datetime import datetime
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from migrate import *

metadata = MetaData()
DeclarativeBase = declarative_base(metadata=metadata)

# New classes and tables
class Journal(DeclarativeBase):
    __tablename__ = 'journal'
    
    # Columns
    id = Column(String(40), primary_key=True)
    domain = Column(Unicode(24))
    user_id = Column(Unicode(40), ForeignKey('users.user_id'))
    text = Column(UnicodeText)
    created = Column(DateTime, default=datetime.now)


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


class Tag(DeclarativeBase):
    __tablename__ = 'tags'
    
    # Columns
    id = Column(Unicode(40), primary_key=True)
    
class Annotable(DeclarativeBase):
    __tablename__ = 'annotables'
    
    # Columns
    id = Column(String(40), primary_key=True)
    association_type = Column(Unicode(50))


class Note(DeclarativeBase):
    __tablename__ = 'notes'
    
    # Columns
    id = Column(String(40), primary_key=True)
    annotable_id = Column(String(40), ForeignKey('annotables.id'))
    user_id = Column(Unicode(40), ForeignKey('users.user_id'))
    text = Column(UnicodeText)
    created = Column(DateTime, default=datetime.now)
    sticky = Column(Boolean, default=False)


def upgrade(migrate_engine):
    """operations to upgrade the db"""
    metadata.bind = migrate_engine

    # Existing classes and tables to be used in relations
    users = Table('users', metadata, autoload=True)

    Journal.__table__.create()

    Taggable.__table__.create()
    Tag.__table__.create()
    taggables_tags_table.create()

    Annotable.__table__.create()
    Note.__table__.create()

def downgrade(migrate_engine):
    """operations to reverse the above upgrade"""
    metadata.bind = migrate_engine

    # Existing classes and tables to be used in relations
    users = Table('users', metadata, autoload=True)

    Journal.__table__.drop()

    taggables_tags_table.drop()
    Tag.__table__.drop()
    Taggable.__table__.drop()

    Note.__table__.drop()
    Annotable.__table__.drop()

