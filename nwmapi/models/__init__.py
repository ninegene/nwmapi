from contextlib import contextmanager
import json
import logging
from sqlalchemy import Unicode, Text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid

log = logging.getLogger(__name__)

# Base is a class and has its own metadata property and its own registry.
# The reason we use 'declarative_base' function to create Base class
# is because that allow us to create another Base class if necessary.
Base = declarative_base()

# establish a constraint naming convention.
# http://docs.sqlalchemy.org/en/latest/core/constraints.html#configuring-constraint-naming-conventions
Base.metadata.naming_convention = {
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    # "ck": "ck_%(table_name)s_%(constraint_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s"
}

# The :class:`.sessionmaker` factory generates new :class:`.Session` objects when called,
# creating them given the configurational arguments established there.
# Session is a session factory class that create session instance to persist and load objects from db.
Session = scoped_session(sessionmaker(
    autoflush=True,
    autocommit=False,
    expire_on_commit=True
))

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    # Use session object to persist and load objects from database
    session = Session()  # invokes sessionmaker.__call__() to create and instance of Session class
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        log.exception('session_scope db error')
        session.rollback()
        raise
    finally:
        session.close()


# Based on: http://docs.sqlalchemy.org/en/rel_1_0/core/custom_types.html#typedecorator-recipes
class CoerceUTF8(TypeDecorator):
    """Safely coerce Python bytestrings to Unicode
    before passing off to the database."""

    impl = Unicode

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            value = value.decode('utf-8')
        return value


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses Postgresql's UUID type, otherwise uses CHAR(32), storing as stringified hex values.
    """

    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value)
            else:
                # hexstring
                return "%.32x" % value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


class JsonBlob(TypeDecorator):
    """JsonBlob is custom type for fields which need to store JSON text."""

    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value