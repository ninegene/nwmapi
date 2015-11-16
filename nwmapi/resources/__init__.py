import logging
from nwmapi.httpstatus import HTTP501NotImplemented

log = logging.getLogger(__name__)

HTTP_METHODS = (
    'CONNECT',
    'DELETE',
    'GET',
    'HEAD',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'TRACE',
)

class BaseHandler(object):
    #: The relative URL this resource should live at.
    __url__ = None

    def on_options(self, req, resp, **kwargs):
        allowed_methods = []

        for method in HTTP_METHODS:
            try:
                responder = getattr(self, 'on_' + method.lower())
            except AttributeError:
                # resource does not implement this method
                pass
            else:
                # Usually expect a method, but any callable will do
                if callable(responder):
                    allowed_methods.append(method)

        allowed = ', '.join(allowed_methods)

        resp.set_header('Allow', allowed)
        resp.http204nocontent()


class RootResource(BaseHandler):
    __url__ = '/'

    def on_get(self, req, resp):
        raise HTTP501NotImplemented()


