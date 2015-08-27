import falcon


def validate_id():
    def hook(req, resp, resource, params):
        id = params['id']
        if len(id) != 32:
            raise falcon.HTTPInvalidParam('The "id" needs to be 32 characters in length', 'id')

    return hook


def max_body(limit):
    def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            msg = ('The size of the request is too large. The body must not '
                   'exceed ' + str(limit) + ' bytes in length.')

            raise falcon.HTTPRequestEntityTooLarge('Request body is too large', msg)

    return hook
