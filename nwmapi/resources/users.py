import logging

import falcon
from nwmapi.common import booleanize
from nwmapi.hooks import require_path_param, validate_fields
from nwmapi.httpstatus import HTTP404NotFound, HTTP501NotImplemented
from nwmapi.models.user import User
from nwmapi.resources import BaseHandler
from nwmapi.services import userservice

log = logging.getLogger(__name__)



# HTTP method   URI Pattern                 Method
# GET           /users                      get_user_list()
# POST          /users                      create_user()
# GET           /users/<id>                 get_user()
# PUT           /users/<id>                 update_user()
# DELETE        /users/<id>                 delete_user()

# TODO

# See: http://docs.aws.amazon.com/AmazonS3/latest/dev/RESTAuthentication.html
# See: http://docs.stormpath.com/rest/product-guide/#account-resource
# See: https://docs.strongloop.com/display/public/LB/User+REST+API

# GET           /users/<id>/accessTokens    get_user_access_tokens()
# POST          /users/<id>/accessTokens    create_user_access_tokens()
# DELETE        /users/<id>/accessTokens    delete_user_access_tokens()
# GET           /users/confirm              confirm_email()
# GET           /users/count                user_count()
# GET           /user/<id>/exists           user_exists()
# POST          /users/login                login_user()
# POST          /users/logout               logout_user()
# POST          /users/reset                reset_password()

# http://docs.stormpath.com/rest/product-guide/#verify-an-email-address
# http://docs.stormpath.com/rest/product-guide/#application-account-authc
# POST          /users/emailVerificationTokens/<token> confirm_email()
# POST          /users/loginAttempts        login_user()
# POST          /users/passwordResetTokens  reset_password()


class UsersResource(BaseHandler):
    #: The relative URL this resource should live at.
    __url__ = '/users'

    # @falcon.before(require_query_param('limit'))
    def on_get(self, req, resp):
        filters = req.params.get('q', None)
        order_by = req.params.get('order_by', None)
        limit = req.params.get('limit', None)
        offset = req.params.get('offset', None)
        start = req.params.get('start', None)
        end = req.params.get('end', None)

        users = userservice.get_user_list(filters=filters, order_by=order_by,
                                          limit=limit, offset=offset, start=start, end=end)

        resp.http200ok(result=users)


    @falcon.before(validate_fields(User))
    def on_post(self, req, resp):
        user = userservice.create_user(req.json_data)
        resp.http201created(location='/users/%s' % user.id.hex, result=user)


class UserResource(BaseHandler):
    __url__ = '/users/{id}'

    @falcon.before(require_path_param('id'))
    def on_get(self, req, resp, id):
        user = userservice.get_user(id=id)

        if user is None:
            raise HTTP404NotFound()

        resp.http200ok(result=user)


    @falcon.before(require_path_param('id'))
    def on_put(self, req, resp, id):
        user = userservice.update_user(req.json_data, id=id)

        if user is None:
            raise HTTP404NotFound()

        resp.http200ok(result=user)


    @falcon.before(require_path_param('id'))
    def on_delete(self, req, resp, id):
        user = userservice.delete_user(id=id)

        if user is None:
            raise HTTP404NotFound()

        resp.http204nocontent()
