import logging

import falcon

log = logging.getLogger(__name__)


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


class HTTP400MissingRequiredParam(falcon.HTTPMissingParam):
    """A parameter is missing from the request. Inherits from ``HTTPBadRequest``.

    This error may refer to a parameter in a query string, form, or
    document that was submitted with the request.

    Args:
        param_name (str): The name of the parameter.
        kwargs (optional): Same as for ``HTTPError``.

    """

    def __init__(self, param_name, **kwargs):
        super(HTTP400MissingRequiredParam, self).__init__(param_name, **kwargs)


class HTTP400InvalidParam(falcon.HTTPInvalidParam):
    """A parameter in the request is invalid. Inherits from ``HTTPBadRequest``.

    This error may refer to a parameter in a query string, form, or
    document that was submitted with the request.

    Args:
        msg (str): A description of the invalid parameter.
        param_name (str): The name of the parameter.
        kwargs (optional): Same as for ``HTTPError``.

    """

    def __init__(self, param_name, **kwargs):
        super(HTTP400InvalidParam, self).__init__("", param_name, **kwargs)


class HTTP403Forbidden(falcon.HTTPForbidden):
    """403 Forbidden.

    Use when the client's credentials are good, but they do not have permission
    to access the requested resource.

    If the request method was not HEAD and the server wishes to make
    public why the request has not been fulfilled, it SHOULD describe the
    reason for the refusal in the entity.  If the server does not wish to
    make this information available to the client, the status code 404
    (Not Found) can be used instead. (RFC 2616)

    Args:
        title (str): Error title (e.g., 'Permission Denied').
        description (str): Human-friendly description of the error, along with
            a helpful suggestion or two.
        kwargs (optional): Same as for ``HTTPError``.

    """

    def __init__(self, title, description, **kwargs):
        super(HTTP403Forbidden, self).__init__(title, description, **kwargs)


class HTTP404NotFound(falcon.HTTPNotFound):
    """404 Not Found.

    Use this when the URL path does not map to an existing resource, or you
    do not wish to disclose exactly why a request was refused.

    """

    def __init__(self, **kwargs):
        super(HTTP404NotFound, self).__init__(**kwargs)


class HTTP405MethodNotAllowed(falcon.HTTPMethodNotAllowed):
    """405 Method Not Allowed.

    The method specified in the Request-Line is not allowed for the
    resource identified by the Request-URI. The response MUST include an
    Allow header containing a list of valid methods for the requested
    resource. (RFC 2616)

    Args:
        allowed_methods (list of str): Allowed HTTP methods for this
            resource (e.g., ``['GET', 'POST', 'HEAD']``).

    """

    def __init__(self, allowed_methods, **kwargs):
        super(HTTP405MethodNotAllowed, self).__init__(**kwargs)


class HTTP406NotAcceptable(falcon.HTTPNotAcceptable):
    """406 Not Acceptable.

    The client requested a resource in a representation that is not
    supported by the server. The client must indicate a supported
    media type in the Accept header.

    The resource identified by the request is only capable of generating
    response entities which have content characteristics not acceptable
    according to the accept headers sent in the request. (RFC 2616)

    Args:
        description (str): Human-friendly description of the error, along with
            a helpful suggestion or two.
        kwargs (optional): Same as for ``HTTPError``.

    """

    def __init__(self, description, **kwargs):
        super(HTTP406NotAcceptable, self).__init__('Media type not acceptable', description, **kwargs)


class HTTP413RequestEntityTooLarge(falcon.HTTPRequestEntityTooLarge):
    """413 Request Entity Too Large.

    The server is refusing to process a request because the request
    entity is larger than the server is willing or able to process. The
    server MAY close the connection to prevent the client from continuing
    the request.

    If the condition is temporary, the server SHOULD include a Retry-
    After header field to indicate that it is temporary and after what
    time the client MAY try again.

    (RFC 2616)

    Args:
        title (str): Error title (e.g., 'Request Body Limit Exceeded').
        description (str): Human-friendly description of the error, along with
            a helpful suggestion or two.
        retry_after (datetime or int, optional): Value for the Retry-After
            header. If a ``datetime`` object, will serialize as an HTTP date.
            Otherwise, a non-negative ``int`` is expected, representing the
            number of seconds to wait. See also: http://goo.gl/DIrWr .
        kwargs (optional): Same as for ``HTTPError``.

    """

    def __init__(self, title, description, retry_after=None, **kwargs):
        super(HTTP413RequestEntityTooLarge, self).__init__(title, description, **kwargs)


class HTTP415UnsupportedMediaType(falcon.HTTPUnsupportedMediaType):
    """415 Unsupported Media Type.

    The client is trying to submit a resource encoded as an Internet media
    type that the server does not support.

    Args:
        description (str): Human-friendly description of the error, along with
            a helpful suggestion or two.
        kwargs (optional): Same as for ``HTTPError``.

    """

    def __init__(self, description, **kwargs):
        super(HTTP415UnsupportedMediaType, self).__init__(description, **kwargs)


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


class HTTP501NotImplemented(falcon.HTTPError):
    """501 Not Implemented.

    Args:
        title (str): Error title, for example: 'Method Not Implemented Yet'.
        description (str): Human-friendly description of the error, along with
            a helpful suggestion or two.
        kwargs (optional): Same as for ``HTTPError``.

    """

    def __init__(self, title=None, description=None, **kwargs):
        title = title or 'Method Not Implemented'
        description = description or ("The server does not support the functionality required to fulfill"
                                      " the request.")
        super(HTTP501NotImplemented, self).__init__(falcon.HTTP_501, title, description, **kwargs)


class HTTP503ServiceUnavailable(falcon.HTTPServiceUnavailable):
    """503 Service Unavailable.

    Args:
        title (str): Error title (e.g., 'Temporarily Unavailable').
        description (str): Human-friendly description of the error, along with
            a helpful suggestion or two.
        retry_after (datetime or int): Value for the Retry-After header. If a
            ``datetime`` object, will serialize as an HTTP date. Otherwise,
            a non-negative ``int`` is expected, representing the number of
            seconds to wait. See also: http://goo.gl/DIrWr .
        kwargs (optional): Same as for ``HTTPError``.

    """

    def __init__(self, title, description, retry_after, **kwargs):
        super(HTTP503ServiceUnavailable, self).__init__(title, description, **kwargs)


def _HTTPError_to_dict(self, obj_type=dict):
    """Returns a basic dictionary representing the error.

    This method can be useful when serializing the error to hash-like
    media types, such as YAML, JSON, and MessagePack.

    Args:
        obj_type: A dict-like type that will be used to store the
            error information (default ``dict``).

    Returns:
        A dictionary populated with the error's title, description, etc.

    """

    assert self.has_representation

    obj = obj_type()

    if self.status is not None:
        obj['status'] = self.status

    if self.title is not None:
        obj['title'] = self.title

    if self.description is not None:
        obj['description'] = self.description

    if self.code is not None:
        obj['code'] = self.code

    if self.link is not None:
        obj['link'] = self.link

    return obj

# Monkey patch to_dict to include 'status' attribute
falcon.HTTPError.to_dict = _HTTPError_to_dict
