import falcon
from nwmapi import UserResource
from nwmapi.errors import handle_server_error, raise_bad_request
from nwmapi.resources import BadRequest
from nwmapi.resources.users import UsersResource


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

    app.add_sink(raise_bad_request)
    app.add_route('/', BadRequest())
    app.add_route('/{method}', BadRequest())

    app.add_route('/users/{id}', user)
    app.add_route('/users', users)

    # If a responder ever raised an instance of Exception, pass control to the given handler.
    app.add_error_handler(Exception, handle_server_error)
