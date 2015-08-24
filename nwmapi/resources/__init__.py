import falcon


class BaseHandler(object):

    def on_options(self, req, resp):
        resp.status = falcon.HTTP_NO_CONTENT
        resp.body = None


class BadRequest(BaseHandler):

    def on_get(self, req, resp):
        raise falcon.HTTPBadRequest(title=falcon.HTTP_BAD_REQUEST,
                                    description='No route handler method defined for the url')


def raise_unknown_url(req, resp):
    raise falcon.HTTPBadRequest(title='Invalid url',
                                description='No route handler method defined for the url')


def respond_json(req, resp, status, result=None, location=None):
    resp.content_type = 'application/json; charset=utf-8'
    resp.status = status
    # Need to explicitly check None, since we want to pass in empty list or object
    if result is not None:
        req.context['result'] = result
    if location:
        resp.location = location
