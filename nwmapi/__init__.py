import falcon
from nwmapi.middleware import RequestResponseLogger, RequireJSON, JSONTranslator
from nwmapi.models import Session, Base
from nwmapi.resources.users import UserResource
from nwmapi.routes import add_routes
from sqlalchemy import engine_from_config


def main(global_config, **settings):
    """ This function returns a WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    Session.configure(bind=engine)
    Base.metadata.bind = engine

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
            RequestResponseLogger(),
            RequireJSON(),
        ])

    add_routes(app)

    return app
