import logging
import falcon
from nwmapi.httpstatus import HTTP500InternalServerError, HTTP400BadRequest
from nwmapi.middleware import ReqRequireJSONType, ParseJSONReqBody, Request, Response, \
    DBSessionLifeCycle, SetCORSRespHeaders, ProcessCommonReqParams
from nwmapi.db import Base, DBSession
from nwmapi.resources import RootResource
from nwmapi.resources.meta import MetaListResource
from nwmapi.resources.users import UserResource, UsersResource
from sqlalchemy import engine_from_config


log = logging.getLogger(__name__)


def main(global_config, **settings):
    """ This function returns a WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    Base.metadata.create_all()

    # Configure WSGI server (app is a WSGI callable)
    app = falcon.API(
        # media type to use as the value for the Content-Type header on responses
        media_type='application/json; charset=utf-8',

        # Middleware components provide a way to execute logic before the framework routes each request,
        # after each request is routed but before the target responder is called, or just before the
        # response is returned for each request. Middleware component's methods (e.g. process_request)
        # are executed hierarchically, as a stack, following the ordering of the list. If one of the
        # process_request middleware methods raises an error, it will be processed according
        # to the error type. If the type matches a registered error handler, that handler will be invoked
        # and then the framework will begin to unwind the stack, skipping any lower layers.
        middleware=[
            DBSessionLifeCycle(),
            ReqRequireJSONType(),
            ProcessCommonReqParams(),
            ParseJSONReqBody(),
            SetCORSRespHeaders(),
        ],

        # ``Request``-like class to use instead of Falcon's default class. Among other things,
        # this feature affords inheriting from ``falcon.request.Request`` in order
        # to override the ``context_type`` class variable.
        # (default ``falcon.request.Request``)
        request_type=Request,
        response_type=Response,
    )

    app.set_error_serializer(json_error_serializer)

    add_routes(app)

    return app


def add_routes(app):
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
    app.add_route(RootResource.__url__, RootResource())
    app.add_route(MetaListResource.__url__, MetaListResource())
    app.add_route(UsersResource.__url__, UsersResource())
    app.add_route(UserResource.__url__, UserResource())

    # If a responder ever raised an instance of Exception, pass control to the given handler.
    app.add_error_handler(Exception, handle_server_error)


def json_error_serializer(req, exception):
    """Override default serialize to always return json representation

       Args:
            req: The request object.

        Returns:
            A ``tuple`` of the form (*media_type*, *representation*), or (``None``, ``None``)
            if the client does not support any of the available media types.
    """
    return 'application/json', exception.to_json()

# A handler can either raise an instance of ``HTTPError``
# or modify `resp` manually in order to communicate
# information about the issue to the client.
def handle_server_error(ex, req, resp, params):
    log.exception(ex)
    http_error = ex

    if not isinstance(ex, falcon.HTTPError):
        description = repr(ex)
        # if hasattr(ex, 'asdict') and callable(ex.asdict):
        #     description = repr(ex.asdict)

        http_error = HTTP500InternalServerError(
            title=repr(type(ex)),
            description=description)

    raise http_error


def raise_unknown_url(req, resp):
    raise HTTP400BadRequest(title='Invalid url',
                            description='No route handler method defined for the url')

