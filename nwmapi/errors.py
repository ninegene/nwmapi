import logging
import falcon
from nwmapi.httpstatus import HTTP400BadRequest, HTTP500InternalServerError
import re

log = logging.getLogger(__name__)


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
        http_error = HTTP500InternalServerError(title=str(type(ex)), description=str(ex.message))

    raise http_error


class UnknownUrl(object):
    def on_get(self, req, resp):
        raise_unknown_url(req, resp)


def raise_unknown_url(req, resp):
    raise HTTP400BadRequest(title='Invalid url',
                            description='No route handler method defined for the url')


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
        try:
            try:
                obj['status'] = int(re.findall(r'^\d+', self.status)[0])
            except:
                obj['status'] = int(self.status)
        except:
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
