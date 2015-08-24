import falcon

def validate_uuid():

    def hook(req, resp, resource, params):
        id = params['id']
        if len(id) != 32:
            raise falcon.HTTPInvalidParam('The "id" needs to be 32 characters in length', 'id')

    return hook


def max_body(limit):

    def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            msg = ('The size of the request is too large. The body must not '
                   'exceed ' + str(limit) + ' bytes in length.')

            raise falcon.HTTPRequestEntityTooLarge('Request body is too large', msg)

    return hook


# import logging
# import falcon
# from nwmapi.models import session_scope
# from nwmapi.models.user import User
# from sqlalchemy import and_
#
#
# def log_request(fun):
#     def wrapper(self, req, resp):
#         logging.info('%s %s %s', req.protocol.upper(), req.method, req.relative_uri)
#         fun(self, req, resp)
#     return wrapper
#
# def check_login_credentials(fun):
#     def wrapper(self, req, resp):
#         # Extract user credentials
#         cookies = req.cookies
#         cookie_token = cookies['api_token'] if ('api_token' in cookies) else None
#         user_id = cookies['user_id'] if ('user_id' in cookies) else None
#
#         if not user_id or not cookie_token:
#             resp.status = falcon.HTTP_401
#             resp.body = "No login credentials present in cookie."
#             self.me = None
#             return
#
#         with session_scope() as db:
#             query = db.query(User).filter(and_(User.id == user_id, User.api_token == cookie_token))
#             if query.count() == 0:
#                 resp.status = falcon.HTTP_401
#                 resp.body = "Login credentials supplied do not match any user in database."
#                 self.me = None
#                 return
#             user = query.first()
#             self.me = user
#         fun(self, req, resp)
#     return wrapper
#
# def before_request(fun):
#     @log_request
#     @check_login_credentials
#     def wrapper(self, req, resp):
#         fun(self, req, resp)
#     return wrapper
