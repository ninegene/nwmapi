from nwmapi.models.user import *
from nwmapi.common import parse_vars, setup_logging, get_appsettings
import os
import sys

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker


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
    engine.echo = True
    Session = sessionmaker(
        autoflush=True,
        autocommit=False,
        expire_on_commit=True
    )
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)

    session = Session()
    count = session.query(User).delete()
    print('deleted %s', count)
    user1 = User()
    user1.username = 'user1'
    user1.email = 'user1@nawama.com'
    session.add(user1)

    user2 = User()
    user2.username = 'user2'
    user2.email = 'user2@nawama.com'
    session.add(user2)
    session.commit()
    print(user1.id, len(str(user1.id)), user1.id.hex, len(user1.id.hex))
    print(user2.id, len(str(user2.id)), user2.id.hex, len(user2.id.hex))
    print(user1.to_dict())
    print(user1.activation)

    # u = session.query(User).filter(User.id == user.id).first()
