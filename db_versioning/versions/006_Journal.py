from datetime import datetime
from sqlalchemy import Table, MetaData
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Unicode, UnicodeText, DateTime, String
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
class Journal(DeclarativeBase):
    __tablename__ = 'journal'
    
    # Columns
    id = Column(String(40), primary_key=True)
    domain = Column(Unicode(24))
    user_id = Column(Unicode(40), ForeignKey('users.user_id'))
    text = Column(UnicodeText)
    created = Column(DateTime, default=datetime.now)


def upgrade():
    # Upgrade operations go here. Don't create your own engine; use the engine
    # named 'migrate_engine' imported from migrate.
    Journal.__table__.create()

def downgrade():
    # Operations to reverse the above upgrade go here.
    Journal.__table__.drop()

