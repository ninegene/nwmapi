import ConfigParser as configparser
from logging.config import fileConfig

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
