import json
import logging
import falcon
# from nwmapi.hooks import max_body, check_context_key
from nwmapi.models import session_scope
from nwmapi.models.user import User

log = logging.getLogger(__name__)


class UserResource:

    def __init__(self):
        pass

    def on_get(self, req, resp):
        user_id = req.get_param('user_id', required=True)
        user = get_user_by_id(user_id)

        if user is None:
            raise falcon.HTTPNotFound()

        # resp.set_header('X-Powered-By', 'Small Furry Creatures')
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(user)

    # @falcon.before(check_context_key('doc'))
    # @falcon.before(max_body(64 * 1024))
    def on_post(self, req, resp):
        doc = req.context['doc']

        user_id = 'my_user_id'
        resp.status = falcon.HTTP_201
        resp.location = '/user/%s' % (user_id)


def get_user_by_id(user_id):
    with session_scope() as db:
        user = db.query(User).filter(User.id == user_id).first()
    return user
