from collections import OrderedDict
import json
import logging
from datetime import datetime
import dateutil.parser
from dateutil.tz import tzutc
from sqlalchemy import Unicode, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID
import uuid

log = logging.getLogger(__name__)

# See: http://docs.sqlalchemy.org/en/rel_1_0/orm/extensions/declarative/mixins.html#augmenting-the-base
class Base(object):
    """A mixin class to augment Base class that will be extended by all Model classes
    """

    @classmethod
    def primary_key(cls):
        return cls.__table__.primary_key.columns.values()[0].name

    def to_dict(self, excluded_columns=set(), included_columns=set()):
        include_all_cols = included_columns is None or len(included_columns) == 0
        result = OrderedDict()
        for col in self.__table__.columns.keys():
            if include_all_cols or col in included_columns:
                if col in excluded_columns:
                    continue

                val = getattr(self, col, None)
                if type(val) is uuid.UUID:
                    result[col] = val.hex
                elif type(val) is datetime:
                    val = val.replace(microsecond=0)
                    result[col] = val.isoformat()
                else:
                    result[col] = getattr(self, col, None)
        return result

    def from_dict(self, dictionary):
        dictionary = dictionary or {}
        for col in self.__table__.columns.keys():
            coltype = self.__table__.columns._data[col].type
            val = dictionary.get(col, None)
            if coltype is DateTime or coltype is UTCDateTime:
                val = dateutil.parser.parse(val)

            if val:
                setattr(self, col, val)

    def replace(self, dictionary):
        dictionary = dictionary or {}
        for col in self.__table__.columns.keys():
            setattr(self, col, None)
        self.from_dict(dictionary)

    @classmethod
    def meta(cls):
        """Return a dictionary containing meta-information about the model."""
        attribute_info = {}
        for name, value in cls.__table__.columns.items():
            attribute_info[name] = str(value.type).lower()

        return {cls.__name__: attribute_info}

    def __str__(self):
        return str(getattr(self, self.primary_key()))

# Base is a class and has its own metadata property and its own registry.
# The reason we use 'declarative_base' function to create Base class
# is because that allow us to create another Base class if necessary.
Base = declarative_base(cls=Base)

# establish a constraint naming convention.
# http://docs.sqlalchemy.org/en/latest/core/constraints.html#configuring-constraint-naming-conventions
Base.metadata.naming_convention = {
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s"
}

# The :class:`.sessionmaker` factory generates new :class:`.Session` objects when called,
# creating them given the configurational arguments established there.

# the scoped_session() is provided which produces a thread-managed registry of Session objects.
# It is commonly used in web applications so that a single global variable can be used to safely
# represent transactional sessions with sets of objects, localized to a single thread.
# scoped_session() maintains a reference to the same session object for instances of Session.

# Session is a session factory class that create session instance to persist and load objects from db.
Session = sessionmaker(  # invokes sessionmaker.__call__() to create and instance of Session class
                         autoflush=True,
                         autocommit=False,
                         expire_on_commit=True
                         )

dbsession = scoped_session(Session)

# @contextmanager
# def transactional_dbsession():
#     """Provide a transactional scope around a series of operations."""
#     # Use session object to persist and load objects from database
#     dbsession = Session()
#     try:
#         yield dbsession
#         dbsession.commit()
#     except SQLAlchemyError as e:
#         log.exception(e)
#         dbsession.rollback()
#         raise


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


# Based on: http://stackoverflow.com/questions/2528189/can-sqlalchemy-datetime-objects-only-be-naive
class UTCDateTime(TypeDecorator):
    impl = DateTime

    def process_bind_param(self, value, engine):
        if type(value) is unicode or type(value) is str:
            value = dateutil.parser.parse(value)
        if value is not None:
            return value.astimezone(tzutc())

    def process_result_value(self, value, engine):
        if type(value) is unicode or type(value) is str:
            value = dateutil.parser.parse(value)
        if value is not None:
            return datetime(value.year, value.month, value.day,
                            value.hour, value.minute, value.second,
                            value.microsecond, tzinfo=tzutc())


# See: https://www.percona.com/blog/2014/12/19/store-uuid-optimized-way/
def ordered_uuid1():
    """
    Returns a UUID type 1 value, with the more constant segments of the
    UUID at the start of the UUID. This allows us to have mostly monotonically
    increasing UUID values, which are much better for INSERT/UPDATE performance
    in the DB.

        UUID                     = time-low "-" time-mid "-"
                                   time-high-and-version "-"
                                   clock-seq-and-reserved
                                   clock-seq-low "-" node
          time-low               = 8hexDigit
          time-mid               = 4hexDigit
          time-high-and-version  = 4hexDigit
          clock-seq-and-reserved = 2hexDigit
          clock-seq-low          = 2hexDigit
          node                   = 12hexDigit

    """
    val = uuid.uuid1().hex
    # 58e0a7d7 eebc 11d8 9669 0800200c9a66 => 11d8 eebc 58e0a7d7 0800200c9a66 9669
    # new_val = val[12:16] + val[8:12] + val[0:8] + val[20:] + val[16:20]
    # 58e0a7d7 eebc 11d8 9669 0800200c9a66 => 0800200c9a66 9669 11d8 eebc 58e0a7d7
    new_val = val[20:] + val[16:20] + val[12:16] + val[8:12] + val[0:8]
    return uuid.UUID(new_val)


def utcnow():
    """
    :return: current datetime in utc with utc timezone
    """
    return datetime.now(tz=tzutc())


class JSONEncoder(json.JSONEncoder):
    """Extend the default JSONEncoder to support ``datetime`` and ``UUID`` as JSON string.

    json.JSONEncoder supports the following objects and types by default:

    +-------------------+---------------+
    | Python            | JSON          |
    +===================+===============+
    | dict              | object        |
    +-------------------+---------------+
    | list, tuple       | array         |
    +-------------------+---------------+
    | str, unicode      | string        |
    +-------------------+---------------+
    | int, long, float  | number        |
    +-------------------+---------------+
    | True              | true          |
    +-------------------+---------------+
    | False             | false         |
    +-------------------+---------------+
    | None              | null          |
    +-------------------+---------------+

    To extend this to recognize other objects, subclass and implement a
    ``.default()`` method with another method that returns a serializable
    object for ``o`` if possible, otherwise it should call the superclass
    implementation (to raise ``TypeError``).

    """

    def default(self, o):
        """Implement this method in a subclass such that it returns a
        serializable object for ``o``, or calls the base implementation (to
        raise a ``TypeError``).

        For example, to support arbitrary iterators, you could implement
        default like this::

            def default(self, o):
                try:
                    iterable = iter(o)
                except TypeError:
                    pass
                else:
                    return list(iterable)
                return JSONEncoder.default(self, o)
        """
        if type(o) is uuid.UUID:
            return o.hex
        elif type(o) is datetime:
            o = o.replace(microsecond=0)
            return o.isoformat()
        return json.JSONEncoder.default(self, o)
