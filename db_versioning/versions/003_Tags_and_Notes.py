from datetime import datetime
from sqlalchemy import Table, MetaData, and_
from sqlalchemy import UniqueConstraint, Column, ForeignKey
from sqlalchemy.types import Unicode, UnicodeText, DateTime, Integer, Boolean
from sqlalchemy.types import String
from sqlalchemy.orm import relation, backref
from migrate import migrate_engine
from migrate.changeset import schema
from migrate.changeset.constraint import ForeignKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

metadata = MetaData()
DeclarativeBase = declarative_base(bind=migrate_engine, metadata=metadata)


# Existing classes and tables to be used in relations
users = Table('users', metadata, autoload=True)

# New classes and tables
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
    created = Column(DateTime, default=datetime.now)
    
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

def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    taggables_tags_table.create()
    Taggable.__table__.create()
    Tag.__table__.create()
    Annotable.__table__.create()
    Note.__table__.create()

def downgrade():
    # Operations to reverse the above upgrade go here.
    taggables_tags_table.drop()
    Taggable.__table__.drop()
    Tag.__table__.drop()
    Annotable.__table__.drop()
    Note.__table__.drop()

