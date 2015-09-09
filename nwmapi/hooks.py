import logging

from nwmapi.httpstatus import HTTP400InvalidParam, HTTP413RequestEntityTooLarge, HTTP400BadRequest, \
    HTTP400MissingRequiredParam
import re

log = logging.getLogger(__name__)


def require_path_param(*args):
    def hook(req, resp, resource, params):
        log.debug('require_path_param %s', params)
        for name in args:
            if name not in params:
                raise HTTP400MissingRequiredParam(name)
            if name == 'id':
                check_id(params)

    def check_id(params):
        val = params.get('id')
        if not re.match("[a-fA-F0-9]{32}$", val):
            raise HTTP400InvalidParam('The "id" needs to be 32 digits hex numbers', 'id')

    return hook


def require_query_param(*args):
    def hook(req, resp, resource, params):
        log.debug('require_query_param %s', req.params)
        for name in args:
            if name not in req.params:
                raise HTTP400MissingRequiredParam(name)

    return hook


def require_req_body():
    def hook(req, resp, resource, params):
        log.debug('require_req_body')
        _check_req_body_exists(req)

    return hook


def _check_req_body_exists(req):
    if req.content_length in (None, 0):
        raise HTTP400BadRequest('Empty request body',
                                'A valid JSON document is required.')


def require_json_fields(*argv):
    def hook(req, resp, resource, params):
        log.debug('require_json_req %s', argv)
        _check_req_body_exists(req)

        data = req.json_data

        for key in argv:
            if key not in data:
                raise HTTP400MissingRequiredParam(key)

    return hook


def validate_fields(model):
    def hook(req, resp, resource, params):
        log.debug('validate_fields')
        _check_req_body_exists(req)

        data = req.json_data

        required_fields = model.required()
        all_fields = required_fields + model.optional()

        for key in data:
            if key not in all_fields:
                raise HTTP400InvalidParam(key)
        for required in set(model.required()):
            if required not in data:
                raise HTTP400MissingRequiredParam(required)
    return hook


def max_body(limit):
    def hook(req, resp, resource, params):
        length = req.content_length
        if length is not None and length > limit:
            description = ('The size of the request is too large. The body must not '
                           'exceed ' + str(limit) + ' bytes in length.')

            raise HTTP413RequestEntityTooLarge('Request body is too large', description)

    return hook
