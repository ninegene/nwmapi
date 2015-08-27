import logging

import falcon

log = logging.getLogger(__name__)


def send_http200_ok(req, resp, result=None):
    _respond_json(req, resp, falcon.HTTP_200, result)


def send_http201_created(req, resp, result=None, location=None):
    _respond_json(req, resp, falcon.HTTP_201, result, location)


def send_http204_nocontent(req, resp):
    _respond_json(req, resp, falcon.HTTP_204)


def _respond_json(req, resp, status, result=None, location=None):
    resp.content_type = 'application/json; charset=utf-8'
    resp.status = status

    # Need to explicitly check None, since we want to pass in empty list or object
    if result is not None:
        req.context['result'] = result

    if location:
        resp.location = location


class HTTP400BadRequest(falcon.HTTPBadRequest):
    """400 Bad Request.

    The request could not be understood by the server due to malformed
    syntax. The client SHOULD NOT repeat the request without
    modifications. (RFC 2616)

    Args:
        title (str): Error title (e.g., 'TTL Out of Range').
        description (str): Human-friendly description of the error, along with
            a helpful suggestion or two.
        kwargs (optional): Same as for ``HTTPError``.

    """

    def __init__(self, title, description, **kwargs):
        super(HTTP400BadRequest, self).__init__(title, description, **kwargs)


class HTTP404NotFound(falcon.HTTPNotFound):
    """404 Not Found.

    Use this when the URL path does not map to an existing resource, or you
    do not wish to disclose exactly why a request was refused.

    """

    def __init__(self, **kwargs):
        super(HTTP404NotFound, self).__init__(**kwargs)


class HTTP500InternalServerError(falcon.HTTPInternalServerError):
    """500 Internal Server Error.

    Args:
        title (str): Error title (e.g., 'This Should Never Happen').
        description (str): Human-friendly description of the error, along with
            a helpful suggestion or two.
        kwargs (optional): Same as for ``HTTPError``.

    """

    def __init__(self, title, description, **kwargs):
        super(HTTP500InternalServerError, self).__init__(title, description, **kwargs)
