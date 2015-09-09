import logging

import falcon
from nwmapi.hooks import require_path_param, validate_fields
from nwmapi.httpstatus import HTTP404NotFound, HTTP501NotImplemented
from nwmapi.models.user import User
from nwmapi.resources import BaseHandler
from nwmapi.services.userservice import UserService

log = logging.getLogger(__name__)


# Method         HTTP method   URL
# get_user_list()    GET           /users
# create_user()      POST          /users
# get_user()         GET           /users/<id>
# update_user()      PATCH         /users/<id>
# replace_user()     PUT           /users/<id>
# delete_user()      DELETE        /users/<id>


class UserListResource(BaseHandler):
    #: The relative URL this resource should live at.
    __url__ = '/users'

    # @falcon.before(require_query_param('limit'))
    def on_get(self, req, resp):
        get_user_list(req, resp)

    @falcon.before(validate_fields(User))
    def on_post(self, req, resp):
        create_user(req, resp)


class UserResource(BaseHandler):
    __url__ = '/users/{id}'

    @falcon.before(require_path_param('id'))
    def on_get(self, req, resp, id):
        get_user(req, resp, id)

    @falcon.before(require_path_param('id'))
    def on_patch(self, req, resp, id):
        update_user(req, resp, id)

    @falcon.before(require_path_param('id'))
    @falcon.before(validate_fields(User))
    def on_put(self, req, resp, id):
        update_user(req, resp, id)

    @falcon.before(require_path_param('id'))
    def on_delete(self, req, resp, id):
        delete_user(req, resp, id)


def get_user_list(req, resp):
    where = req.params.get('where', None)
    order_by = req.params.get('order_by', None)
    limit = req.params.get('limit', None)
    offset = req.params.get('offset', None)
    start = req.params.get('start', None)
    end = req.params.get('end', None)

    service = UserService()
    users = service.get_user_list(where=where,
                                  order_by=order_by,
                                  limit=limit, offset=offset, start=start, end=end)

    resp.http200ok(result=users)


def create_user(req, resp):
    data = req.json_data

    service = UserService()
    user = service.create_user(data)

    resp.http201created(location='/users/%s' % user.id.hex, result=user)


def get_user(req, resp, id):
    service = UserService()
    user = service.get_user(id=id)

    if user is None:
        raise HTTP404NotFound()

    resp.http200ok(result=user)


def update_user(req, resp, id):
    data = req.json_data

    service = UserService()
    user = service.update_user(data, id=id)

    resp.http200ok(result=user)


def delete_user(req, resp, id):
    service = UserService()
    user = service.delete_user(id=id)

    if user is None:
        raise HTTP404NotFound()

    resp.http204nocontent()
