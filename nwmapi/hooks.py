from nwmapi.httpstatus import HTTP400InvalidParam, HTTP413RequestEntityTooLarge, HTTP400BadRequest, \
    HTTP400MissingParam


def require_uuid():
    def hook(req, resp, resource, params):
        uuid = params.get('uuid')
        if uuid is None:
            raise HTTP400MissingParam('uuid')

        if len(uuid) != 32:
            raise HTTP400InvalidParam('The "uuid" needs to be 32 characters in length', 'uuid')

    return hook


def require_req_body():
    def hook(req, resp, resource, params):
        if req.content_length in (None, 0):
            raise HTTP400BadRequest('Empty request body',
                                    'A valid JSON document is required.')
    return hook


def max_body(limit):
    def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            description = ('The size of the request is too large. The body must not '
                           'exceed ' + str(limit) + ' bytes in length.')

            raise HTTP413RequestEntityTooLarge('Request body is too large', description)

    return hook
