import logging

import falcon
from nwmapi import UserResource
from nwmapi.httpstatus import HTTP500InternalServerError, HTTP400BadRequest
from nwmapi.resources.users import UsersResource

log = logging.getLogger(__name__)

# A handler can either raise an instance of ``HTTPError``
# or modify `resp` manually in order to communicate
# information about the issue to the client.
def handle_server_error(ex, req, resp, params):
    log.exception(ex)
    http_error = ex

    if not isinstance(ex, falcon.HTTPError):
        http_error = HTTP500InternalServerError(title=type(ex), description=str(ex))

    raise http_error


class UnknownUrl(object):
    def on_get(self, req, resp):
        raise_unknown_url(req, resp)


def raise_unknown_url(req, resp):
    raise HTTP400BadRequest(title='Invalid url',
                            description='No route handler method defined for the url')


def add_routes(app):
    user = UserResource()
    users = UsersResource()

    # The router treats URI paths as a tree of URI segments and searches by
    # checking the URI one segment at a time. Instead of interpreting the route
    # tree for each look-up, it generates inlined, bespoke Python code to
    # perform the search, then compiles that code. This makes the route
    # processing quite fast.

    # The following notes are taken from comment with routing logic code base of falcon v0.3.0

    # NOTE(kgriffs): Falcon does not support the following:
    #
    #   /foo/{thing1}
    #   /foo/{thing2}
    #
    # On the other hand, this is OK:
    #
    #   /foo/{thing1}
    #   /foo/all
    #
    # NOTE(kgriffs): We don't allow multiple simple var nodes
    # to exist at the same level, e.g.:
    #
    #   /foo/{id}/bar
    #   /foo/{name}/bar
    #

    app.add_sink(raise_unknown_url)
    app.add_route('/', UnknownUrl())
    app.add_route('/{method}', UnknownUrl())

    app.add_route('/users/{id}', user)
    app.add_route('/users', users)

    # If a responder ever raised an instance of Exception, pass control to the given handler.
    app.add_error_handler(Exception, handle_server_error)
