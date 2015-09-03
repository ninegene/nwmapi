import logging

import falcon
from nwmapi.hooks import require_json_keys, require_query_param, require_path_param
from nwmapi.httpstatus import HTTP404NotFound, HTTP501NotImplemented
from nwmapi.resources import BaseHandler
from nwmapi.services.userservice import UserService

log = logging.getLogger(__name__)


# Method         HTTP method   URL
# get_users()    GET           /users
# create_user()  POST          /users
# get_user()     GET           /users/<id>
# replace_user() PUT           /users/<id>
# update_user()  POST          /users/<id>
# delete_user()  DELETE        /users/<id>


class UserListResource(BaseHandler):
    @falcon.before(require_query_param('limit'))
    def on_get(self, req, resp):
        get_user_list(req, resp)

    @falcon.before(require_json_keys('username', 'email'))
    def on_post(self, req, resp):
        create_user(req, resp)


class UserResource(BaseHandler):
    @falcon.before(require_path_param('id'))
    def on_get(self, req, resp, id):
        get_user(req, resp, id)

    @falcon.before(require_path_param('id'))
    def on_put(self, req, resp, id):
        update_user(req, resp, id)

    @falcon.before(require_path_param('id'))
    @falcon.before(require_json_keys('username', 'email'))
    def on_post(self, req, resp, id):
        replace_user(req, resp, id)

    @falcon.before(require_path_param('id'))
    def on_delete(self, req, resp, id):
        delete_user(req, resp, id)


def get_user_list(req, resp):
    limit = req.params['limit']
    s = UserService(req.dbsession)

    users = s.get_user_list(limit=limit)
    resp.http200ok(result=users)


def create_user(req, resp):
    s = UserService(req.dbsession)

    data = req.json_data
    user = s.create_user(data)

    resp.http201created(location='/users/%s' % user.id.hex)


def get_user(req, resp, id):
    s = UserService(req.dbsession)
    user = s.get_user(id=id)

    if user is None:
        raise HTTP404NotFound()

    resp.http200ok(result=user)


def replace_user(req, resp, id):
    raise HTTP501NotImplemented()


def update_user(req, resp, id):
    s = UserService(req.dbsession)
    user = s.get_user(id=id)


def delete_user(req, resp, id):
    s = UserService(req.dbsession)
    user = s.delete_user(id=id)

    if user is None:
        raise HTTP404NotFound()

    resp.http204nocontent(resp)
