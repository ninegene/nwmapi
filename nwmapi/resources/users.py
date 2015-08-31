import logging

import falcon
from nwmapi.hooks import require_json_keys, require_req_body, require_query_param, require_path_param
from nwmapi.httpstatus import HTTP404NotFound, send_http200_ok, HTTP501NotImplemented
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


class UsersResource(BaseHandler):
    @falcon.before(require_query_param('limit'))
    def on_get(self, req, resp):
        get_users(req, resp)

    @falcon.before(require_json_keys('username', 'email'))
    def on_post(self, req, resp):
        create_user(req, resp)


class UserResource(BaseHandler):
    @falcon.before(require_path_param('id'))
    def on_get(self, req, resp, id):
        get_user(req, resp, id)

    @falcon.before(require_path_param('id'))
    @falcon.before(require_json_keys('username', 'email'))
    def on_put(self, req, resp, id):
        replace_user(req, resp, id)

    @falcon.before(require_path_param('id'))
    @falcon.before(require_req_body())
    def on_post(self, req, resp, id):
        update_user(req, resp, id)

    @falcon.before(require_path_param('id'))
    def on_delete(self, req, resp, id):
        delete_user(req, resp, id)


def get_users(req, resp):
    limit = req.params['limit']
    s = UserService(req.dbsession)

    users = s.get_user_list(limit=limit)
    result = [user.to_dict() for user in users]

    send_http200_ok(req, resp, result)


def create_user(req, resp):
    s = UserService(req.dbsession)

    log.debug(req.json)
    raise HTTP501NotImplemented()
    # user_id = 'test'
    # send_http201_created(req, resp, location='/user/' + user_id)


def get_user(req, resp, id):
    s = UserService(req.dbsession)
    user = s.get_user(id=id)

    if user is None:
        raise HTTP404NotFound()

    result = user.to_dict()
    send_http200_ok(req, resp, result)


def replace_user(req, resp, id):
    raise HTTP501NotImplemented()
    # send_http200_ok(req, resp, result=None)


def update_user(req, resp, id):
    raise HTTP501NotImplemented()
    # send_http200_ok(req, resp, result=None)


def delete_user(req, resp, id):
    raise HTTP501NotImplemented()
    # send_http200_ok(req, resp, result=None)
