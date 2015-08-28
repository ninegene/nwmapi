import logging

import falcon
from nwmapi.hooks import require_uuid, require_req_body
from nwmapi.httpstatus import HTTP404NotFound, send_http200_ok, send_http201_created, HTTP400MissingParam
from nwmapi.resources import BaseHandler
from nwmapi.services.userservice import UserService

log = logging.getLogger(__name__)


class UserResource(BaseHandler):
    @falcon.before(require_uuid())
    def on_get(self, req, resp, uuid):

        user = UserService.get_user(id=id)

        if user is None:
            raise HTTP404NotFound()

        send_http200_ok(req, resp, user)

    @falcon.before(require_uuid())
    def on_put(self, req, resp, id):
        doc = req.context['doc']

        # TODO: update user

        send_http200_ok(req, resp)

    @falcon.before(require_uuid())
    def on_delete(self, req, resp, id):

        # TODO: delete user

        send_http200_ok(req, resp)


class UsersResource(BaseHandler):
    def on_get(self, req, resp):
        users = UserService.get_user_list()

        # Todo: support limit and offset

        send_http200_ok(req, resp, users)

    @falcon.before(require_req_body())
    def on_post(self, req, resp):
        doc = req.context['doc']

        # TODO: create user
        user_id = 'test'
        send_http201_created(req, resp, location='/user/' + user_id)
