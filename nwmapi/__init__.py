from contextlib import contextmanager
import falcon
from nwmapi.middleware.auth import RequireAuthToken
from nwmapi.middleware.contenttype import RequireJSON, JSONTranslator
from nwmapi.resources.user import UserResource
from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


BaseModel = declarative_base()
# establish a constraint naming convention.
# http://docs.sqlalchemy.org/en/latest/core/constraints.html#configuring-constraint-naming-conventions
#
BaseModel.metadata.naming_convention={
    "pk": "pk_%(table_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ix": "ix_%(table_name)s_%(column_0_name)s"
}

DBSession = scoped_session(sessionmaker(
    autoflush=True,
    autocommit=False,
    expire_on_commit=True))


@contextmanager
def dbsession_scope():
    """Provide a transactional scope around a series of operations."""
    session = DBSession()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def main(global_config, **settings):
    """ This function returns a WSGI application.
    """
    settings = {'sqlalchemy.url': 'sqlite:///nwmdb.sqlite', 'apiversion': '1'}
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    BaseModel.metadata.bind = engine

    # Configure WSGI server (app is a WSGI callable)
    app = falcon.API(middleware=[
        RequireAuthToken(),
        RequireJSON(),
        JSONTranslator()
    ])

    user = UserResource()

    api_version = '/api/' + settings['apiversion']
    app.add_route(api_version + '/user', user)

    return app
