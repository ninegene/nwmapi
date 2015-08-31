import ConfigParser as configparser
import hashlib
from logging.config import fileConfig
import random
import uuid
from datetime import datetime
from dateutil.tz import tzutc

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


# See also:https://www.percona.com/blog/2014/12/19/store-uuid-optimized-way/
# Taken from: https://github.com/procession/procession/blob/master/procession/helpers.py
def ordered_uuid1():
    """
    Returns a UUID type 1 value, with the more constant segments of the
    UUID at the start of the UUID. This allows us to have mostly monotonically
    increasing UUID values, which are much better for INSERT/UPDATE performance
    in the DB.

    A UUID1 hex looks like:

        '27392da2-8bae-11e4-961d-e06995034837'

    From this, we need to take the last two segments, which represent the more
    constant information about the node we're on, and place those first in the
    new UUID's bytes. We then take the '11e4' segment, which represents the
    most significant bits of the timestamp part of the UUID, prefixed with a
    '1' for UUID type, and place that next, followed by the second segment and
    finally the first segment, which are the next most significant bits of the
    timestamp 60-bit number embedded in the UUID.

    So, we convert the above hex to this instead:

        '961de069-9503-4837-11e4-8bae27392da2'

    """
    val = uuid.uuid1().hex
    new_val = val[16:] + val[12:16] + val[8:12] + val[0:8]
    return uuid.UUID(new_val)


def utcnow():
    """
    :return: current datetime in utc with utc timezone
    """
    return datetime.now(tz=tzutc())