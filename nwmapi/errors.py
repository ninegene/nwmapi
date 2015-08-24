import logging
import falcon
import re

log = logging.getLogger(__name__)

# class APIError(HTTPError):
#     def __init__(self, status, title=None, description=None, headers=None,
#                  href=None, href_text=None, code=None, ex=None):
#         # status (str): HTTP status line, e.g. '404 Not Found'.
#         # title (str): Error title to send to the client. Will be ``None`` if the error should result
#         #              in an HTTP response with an empty body.
#         # description (str): Description of the error to send to the client.
#         # headers (dict): Extra headers to return in the response to the client (default ``None``).
#         # href (str): A URL someone can visit to find out more information
#         #            (default ``None``). Unicode characters are percent-encoded.
#         # href_text (str): If href is given, use this as the friendly title/description for the link
#         #                  (defaults to "API documentation for this error").
#         # code (int): An internal code that customers can reference in their support request or to help
#         #             them when searching for knowledge base articles related to this error
#         #             (default ``None``).
#         self.status = status
#         self.title = title
#         self.description = description
#         self.headers = headers
#         self.href = href
#         self.href_text = href_text
#         self.code = code


# A handler can either raise an instance of ``HTTPError``
# or modify `resp` manually in order to communicate
# information about the issue to the client.
def handle_server_error(ex, req, resp, params):
    log.exception(ex)
    http_error = ex

    if not isinstance(ex, falcon.HTTPError):
        http_error = falcon.HTTPInternalServerError(falcon.HTTP_500, '{} {}'.format(type(ex), ex.message))

    raise http_error


def raise_bad_request(req, resp):
    log.error('raise_unknown_resource: %s %s %s', req.protocol.upper(), req.method, req.relative_uri)
    raise falcon.HTTPBadRequest(title='Unknown Resource',
                                description='No handler found for this url resource')



# def _getattr(obj, attr_name, default_value=None):
#     if attr_name in obj:
#         return getattr(obj, attr_name)
#     return default_value



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