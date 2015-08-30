import ConfigParser as configparser
import hashlib
from logging.config import fileConfig
import random

import os
from paste.deploy import (
    appconfig,
)


# Taken from pyramid framework <pyramid/scripts/common.py>
def parse_vars(args):
    """
    Given variables like ``['a=b', 'c=d']`` turns it into ``{'a':
    'b', 'c': 'd'}``
    """
    result = {}
    for arg in args:
        if '=' not in arg:
            raise ValueError(
                'Variable assignment %r invalid (no "=")'
                % arg)
        name, value = arg.split('=', 1)
        result[name] = value
    return result


def setup_logging(config_uri, fileConfig=fileConfig,
                  configparser=configparser):
    """
    Set up logging via the logging module's fileConfig function with the
    filename specified via ``config_uri`` (a string in the form
    ``filename#sectionname``).

    ConfigParser defaults are specified for the special ``__file__``
    and ``here`` variables, similar to PasteDeploy config loading.
    """
    path, _ = _getpathsec(config_uri, None)
    parser = configparser.ConfigParser()
    parser.read([path])
    if parser.has_section('loggers'):
        config_file = os.path.abspath(path)
        return fileConfig(
            config_file,
            dict(__file__=config_file, here=os.path.dirname(config_file))
        )


def _getpathsec(config_uri, name):
    if '#' in config_uri:
        path, section = config_uri.split('#', 1)
    else:
        path, section = config_uri, 'main'
    if name:
        section = name
    return path, section


def get_appsettings(config_uri, name=None, options=None, appconfig=appconfig):
    """ Return a dictionary representing the key/value pairs in an ``app``
    section within the file represented by ``config_uri``.

    ``options``, if passed, should be a dictionary used as variable assignments
    like ``{'http_port': 8080}``.  This is useful if e.g. ``%(http_port)s`` is
    used in the config file.

    If the ``name`` is None, this will attempt to parse the name from
    the ``config_uri`` string expecting the format ``inifile#name``.
    If no name is found, the name will default to "main"."""
    path, section = _getpathsec(config_uri, name)
    config_name = 'config:%s' % path
    here_dir = os.getcwd()
    return appconfig(
        config_name,
        name=section,
        relative_to=here_dir,
        global_conf=options)


def get_random_alphanumeric(size):
    word = ''
    for i in xrange(size):
        word += random.choice(('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'))
    return word


def gen_random_hash(size=32):
    """Generate a random chars hash. default to 32 chars"""
    assert 1 < size <= 64

    m = hashlib.sha256()
    m.update(get_random_alphanumeric(size))
    return unicode(m.hexdigest()[:size])

# to json code taken from:
# https://github.com/kolypto/py-flask-jsontools/blob/master/flask_jsontools/formatting.py

# region SqlAlchemy Tools
# try:
#     from sqlalchemy import inspect
#     from sqlalchemy.orm.state import InstanceState
# except ImportError as e:
#     def __nomodule(*args, **kwargs):
#         raise e
#
#     inspect = __nomodule
#     InstanceState = __nomodule


from sqlalchemy import inspect
from sqlalchemy.orm.state import InstanceState

def get_entity_propnames(entity):
    """ Get entity property names
        :param entity: Entity
        :type entity: sqlalchemy.ext.declarative.api.DeclarativeMeta
        :returns: Set of entity property names
        :rtype: set
    """
    ins = entity if isinstance(entity, InstanceState) else inspect(entity)
    return set(
        ins.mapper.column_attrs.keys() +  # Columns
        ins.mapper.relationships.keys()  # Relationships
    )


def get_entity_loaded_propnames(entity):
    """ Get entity property names that are loaded (e.g. won't produce new queries)
        :param entity: Entity
        :type entity: sqlalchemy.ext.declarative.api.DeclarativeMeta
        :returns: Set of entity property names
        :rtype: set
    """
    ins = inspect(entity)
    keynames = get_entity_propnames(ins)

    # If the entity is not transient -- exclude unloaded keys
    # Transient entities won't load these anyway, so it's safe to include all columns and get defaults
    if not ins.transient:
        keynames -= ins.unloaded

    # If the entity is expired -- reload expired attributes as well
    # Expired attributes are usually unloaded as well!
    if ins.expired:
        keynames |= ins.expired_attributes

    # Finish
    return keynames


class JsonSerializableBase(object):
    """ Declarative Base mixin to allow objects serialization
        Defines interfaces utilized by :cls:ApiJSONEncoder
    """

    def __json__(self, exluded_keys=set()):
        return {name: getattr(self, name)
                for name in get_entity_loaded_propnames(self) - exluded_keys}

# endregion
