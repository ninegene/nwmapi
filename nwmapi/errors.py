import logging
import falcon

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
    http_error = ex

    if not isinstance(ex, falcon.HTTPError):
        http_error = falcon.HTTPInternalServerError(falcon.HTTP_500, ex.message)

    raise http_error


# def _getattr(obj, attr_name, default_value=None):
#     if attr_name in obj:
#         return getattr(obj, attr_name)
#     return default_value

#
# class RootHandler(object):
#
#     def on_options(self, req, resp):
#         respondJson(resp, falcon.HTTP_204, jsonSuccess())
#
#
# class NoMethod(RootHandler):
#
#     def on_get(self, req, resp):
#         respondJson(resp, falcon.HTTP_400, jsonError('No method in url.'))
#
#
# class UnknownMethod(RootHandler):
#
#     def on_get(self, req, resp, method):
#         respondJson(resp,
#                     falcon.HTTP_400,
#                     jsonError('Unknown method {0!r} in url.'.format(method)))
#
#
# def raise_unknown_url(req, resp):
#     raise UnknownURL()
#
#
# def jsonSuccess(*args, **kwargs):
#     return formatXML(Elt('success', *args, **kwargs))
#
#
# def jsonError(msg):
#     return formatXML(Elt('error', attrib={'reason': msg}))
#
#
# def respondJson(resp, status, body):
#     resp.content_type = 'application/xml; charset=utf-8'
#     resp.status = status
#     resp.body = body
