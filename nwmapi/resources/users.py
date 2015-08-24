import logging
import falcon
from nwmapi.hooks import max_body, validate_uuid
from nwmapi.models import session_scope
from nwmapi.models.user import User
from nwmapi.resources import BaseHandler, respond_json

log = logging.getLogger(__name__)


class UserResource(BaseHandler):

    @falcon.before(validate_uuid())
    def on_get(self, req, resp, id):
        if id is None:
            raise falcon.HTTPMissingParam('id')

        user = get_user_by_id(id)

        if user is None:
            raise falcon.HTTPNotFound(title="User Not Found",
                                      description='Fail to lookup user')

        respond_json(req, resp, falcon.HTTP_200, result=user)

    @falcon.before(max_body(64 * 1024))
    def on_post(self, req, resp, id):
        doc = req.context['doc']

        # TODO: update user

        respond_json(req, resp, falcon.HTTP_201, location='/user/%s' % (id))


class UsersResource(BaseHandler):

    # Todo: support limit and offset
    def on_get(self, req, resp):
        email = req.get_param('email')

        users = get_users_email(email)

        respond_json(req, resp, falcon.HTTP_200, result=users)


def get_user_by_id(id):
    with session_scope() as db:
        user = db.query(User).filter(User.id == id).first()
    return user

def get_users_email(email):
    with session_scope() as db:
        users = db.query(User).filter(User.email == email).all()
        assert len(users) == 0 or len(users) == 1  # we expect to get only one user if exists
    return users

def get_users_username(username):
    with session_scope() as db:
        users = db.query(User).filter(User.username == username).all()
        assert len(users) == 0 or len(users) == 1  # we expect to get only one user if exists
    return users
