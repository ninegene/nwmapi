from collections import OrderedDict
import json
import logging
from datetime import datetime
import uuid

import dateutil.parser
from dateutil.tz import tzutc
from nwmapi.search import create_query
from sqlalchemy import Unicode, Text, DateTime, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID

log = logging.getLogger(__name__)

# See: http://docs.sqlalchemy.org/en/rel_1_0/orm/extensions/declarative/mixins.html#augmenting-the-base
class Base(object):
    """A mixin class to augment Base class that will be extended by all Model classes
    """

    @classmethod
    def required(cls):
        """Return a list of all columns required by the database to create the resource.

        :param cls: The Model class to gather attributes from
        :rtype: list
        """
        columns = []
        for column in cls.__table__.columns:
            if not column.nullable and not column.primary_key:
                columns.append(column.name)
        return columns

    @classmethod
    def optional(cls):
        """Return a list of all nullable columns for the resource's table.

        :rtype: list
        """
        columns = []
        for column in cls.__table__.columns:
            if column.nullable:
                columns.append(column.name)
        return columns

    def primary_key(self):
        """Return the name of the model's primary key field.

        :rtype: string
        """
        return list(self.__table__.primary_key.columns)[0].name

    def to_dict(self, excluded=None, included=None, object_type=dict):
        """Return the resource as a dictionary.
        Include all columns if include_columns is None or empty set
        if a column name is specified in both excluded and included sets,
        the column will get excluded.

        :rtype: dict
        """
        excluded = excluded or set()
        included = included or set()

        columns = self.__table__.columns.keys()
        if len(included) == 0:
            included = set(columns)

        result = object_type()
        for col in columns:
            val = getattr(self, col, None)
            if type(val) is uuid.UUID:
                val = val.hex
            elif type(val) is datetime:
                # val = val.replace(microsecond=0)
                # val = val.isoformat()
                val = val.strftime('%Y-%m-%dT%H:%M:%S.%f')
                val = val[:-3] + 'Z'
            if col in included and col not in excluded:
                result[col] = val
        return result

    def from_dict(self, dictionary):
        dictionary = dictionary or {}
        for col in self.__table__.columns.keys():
            val = dictionary.get(col, None)
            coltype = self.__table__.columns._data[col].type
            valtype = type(val)
            if (valtype is str or valtype is unicode) and (coltype is DateTime or coltype is UTCDateTime):
                val = dateutil.parser.parse(val)
            if val:
                setattr(self, col, val)

    def to_json(self, excluded=None, included=None, pretty=False, object_type=OrderedDict):
        dictionary = self.to_dict(excluded=excluded, included=included, object_type=object_type)
        obj = self.to_dict(OrderedDict)
        if pretty:
            return json.dumps(dictionary, indent=4, separators=(',', ': '), ensure_ascii=False)
        return json.dumps(dictionary)

    def from_json(self, json_str):
        dictionary = json.loads(json_str, encoding='utf-8')
        self.from_dict(dictionary)

    def replace(self, dictionary):
        dictionary = dictionary or {}
        for col in self.__table__.columns.keys():
            setattr(self, col, None)
        self.from_dict(dictionary)

    @classmethod
    def description(cls):
        """Return a field->data type dictionary describing this model
        as reported by the database.

        :rtype: dict
        """

        description = OrderedDict()
        for column in cls.__table__.columns:
            column_description = str(column.type)
            if not column.nullable:
                column_description += ' (required)'
            description[column.name] = column_description
        return description

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
# sessionmaker invokes sessionmaker.__call__() to create and instance of Session class
DBSession = scoped_session(sessionmaker(
    autoflush=True,
    autocommit=False,
    expire_on_commit=True
))

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


# class ModelJSONEncoder(json.JSONEncoder):
#     """Extend the default JSONEncoder to support ``datetime`` and ``UUID`` as JSON string.
#
#     json.JSONEncoder supports the following objects and types by default:
#
#     +-------------------+---------------+
#     | Python            | JSON          |
#     +===================+===============+
#     | dict              | object        |
#     +-------------------+---------------+
#     | list, tuple       | array         |
#     +-------------------+---------------+
#     | str, unicode      | string        |
#     +-------------------+---------------+
#     | int, long, float  | number        |
#     +-------------------+---------------+
#     | True              | true          |
#     +-------------------+---------------+
#     | False             | false         |
#     +-------------------+---------------+
#     | None              | null          |
#     +-------------------+---------------+
#
#     To extend this to recognize other objects, subclass and implement a
#     ``.default()`` method with another method that returns a serializable
#     object for ``o`` if possible, otherwise it should call the superclass
#     implementation (to raise ``TypeError``).
#
#     """
#
#     def default(self, o):
#         """Implement this method in a subclass such that it returns a
#         serializable object for ``o``, or calls the base implementation (to
#         raise a ``TypeError``).
#
#         For example, to support arbitrary iterators, you could implement
#         default like this::
#
#             def default(self, o):
#                 try:
#                     iterable = iter(o)
#                 except TypeError:
#                     pass
#                 else:
#                     return list(iterable)
#                 return JSONEncoder.default(self, o)
#         """
#         if type(o) is uuid.UUID:
#             return o.hex
#         elif type(o) is datetime:
#             o = o.replace(microsecond=0)
#             return o.isoformat()
#         return json.JSONEncoder.default(self, o)


# class ModelJSONDecoder(json.JSONDecoder):
#     def __init__(self, *args, **kwargs):
#         json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
#
#     def object_hook(self, obj):
#         # do something based on obj
#         return obj

def jsonify(result, **kwargs):
    if type(result) is list:
        result = [m.to_dict() if isinstance(m, Base) else m for m in result]
    elif isinstance(result, Base):
        result = result.to_dict()
    # return json.dumps(result, cls=ModelJSONEncoder, encoding='utf-8', **kwargs)
    return json.dumps(result, encoding='utf-8', **kwargs)


def generate_query(model,
                   filters=None, order_by=None, limit=None, offset=None, start=None, end=None):
    """apply where/order_by/limit/offset to the ``Query`` based on a "
    "range and return the newly resulting ``Query``."""

    q = DBSession.query(model)
    if filters:
        q = apply_filters(q, model, filters)
    if order_by:
        q = apply_order_by(q, model, order_by)
    if limit:
        q = q.limit(int(limit))
    if offset:
        q = q.offset(int(offset))
    if start or end:
        if start:
            start = int(start)
        if end:
            end = int(end)
        # apply LIMIT/OFFSET to the ``Query`` based on a range
        q = q.slice(start, end)

    return q


def apply_filters(q, model, filters):
    if filters:
        if type(filters) is list:
            filters = ','.join(filters)
        searchparams = json.loads(filters)
        q = create_query(DBSession, model, searchparams)

    return q


def apply_order_by(q, model, order_by):
    if order_by:
        cols = []
        if type(order_by) is str or type(order_by) is unicode:
            if ',' in order_by:
                cols = order_by.split(',')
            else:
                cols.append(order_by)
        else:
            cols = order_by

        for order_by in cols:
            if order_by.lower().endswith(' desc'):
                q = q.order_by(desc(getattr(model, order_by.strip().split(' ')[0])))
            elif order_by.lower().endswith(' asc'):
                q = q.order_by(getattr(model, order_by.strip().split(' ')[0]))
            else:
                q = q.order_by(getattr(model, order_by))

    return q

