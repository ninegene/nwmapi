from nwmapi import Session, Base
from nwmapi.models import session_scope
from nwmapi.models.user import User
from nwmapi.util.common import parse_vars, setup_logging, get_appsettings
import os
import sys

from sqlalchemy import engine_from_config

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
    with session_scope() as db:
        count = db.query(User).delete()
        print('deleted %s', count)
        testuser = User(fullname='Test User', username='testuser', email="testuser@email.com")
        db.add(testuser)