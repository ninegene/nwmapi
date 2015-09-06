import logging
import json

import falcon
from nwmapi.common import booleanize
from nwmapi.httpstatus import HTTP400BadRequest, HTTP406NotAcceptable, HTTP415UnsupportedMediaType, \
    HTTP500InternalServerError
from nwmapi.db import DBSession, Base, jsonify

log = logging.getLogger(__name__)


class DBSessionLifeCycle(object):
    def process_request(self, req, resp):
        log_debug(req, 'DBSessionLifeCycle: before routing request')

    def process_response(self, req, resp, resource):
        log_debug(req, 'DBSessionLifeCycle: after processing response')
        DBSession.close()


class SetCORSRespHeaders(object):
    def process_response(self, req, resp, resource):
        log_debug(req, 'SetCORSRespHeaders: after processing response')
        # http://stackoverflow.com/questions/10636611/how-does-access-control-allow-origin-header-work
        # http://stackoverflow.com/questions/24687313/what-exactly-does-the-access-control-allow-credentials-header-do
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Credentials', 'true')


class ReqRequireJSONType(object):
    def process_request(self, req, resp):
        log_debug(req, 'RequireJSONType: before routing request')
        if not req.client_accepts_json:
            raise HTTP406NotAcceptable('Unsupported response encoding', href='https://url/to/docs')

        if req.method in ('POST', 'PUT'):
            if not req.content_type or 'application/json' not in req.content_type:
                raise HTTP415UnsupportedMediaType('Unsupported content type', href='https://url/to/docs')


class ProcessCommonReqParams(object):
    def process_request(self, req, resp):
        log_debug(req, 'ParseCommonReqParams: before routing request')
        resp.pretty_json = booleanize(req.params.get('pretty', False))
        if 'pretty' not in req.params and 'pretty' in req.query_string.split('&'):
            resp.pretty_json = True


class ParseJSONReqBody(object):
    def process_request(self, req, resp):
        log_debug(req, 'ParseJSONReqBody: before routing request')
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes form the request body
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            # Nothing to do
            return

        body = req.stream.read()
        if not body:
            raise HTTP400BadRequest(
                title='Empty request body',
                description='A valid JSON document is required.')

        try:
            req.body = body
            req.json_data = json.loads(body)
        # except (ValueError, UnicodeDecodeError):
        except Exception as e:
            log.exception(e)
            raise HTTP400BadRequest(
                title='Malformed JSON',
                description='Could not decode the request body. '
                            'The JSON was incorrect or not encoded as UTF-8')


def log_debug(req, msg):
    log.debug('%s %s %s %s', msg, req.protocol.upper(), req.method, req.relative_uri)


class Request(falcon.Request):
    """Override falcon.Request to provide 'body' and 'json_data' attribute on request object"""

    def __init__(self, env, options=None):
        super(Request, self).__init__(env, options)
        self.body = None
        self.json_data = None


class Response(falcon.Response):
    """Override falcon.Response to provide wrapper methods to return 2xx status and result"""

    def __init__(self):
        self.pretty_json = False
        super(Response, self).__init__()

    def http200ok(self, result=None):
        self._send_json(falcon.HTTP_200, result)

    def http201created(self, result=None, location=None):
        self._send_json(falcon.HTTP_201, result=result, location=location)

    def http204nocontent(self):
        self._send_json(falcon.HTTP_204)

    def _send_json(self, status, result=None, location=None):
        self.content_type = 'application/json; charset=utf-8'
        self.status = status

        if location:
            self.location = location

        # Need to explicitly check None, since we want to pass in empty list or object
        if result is not None:
            try:
                if self.pretty_json:
                    self.body = jsonify(result, indent=4, separators=(',', ': '))
                else:
                    self.body = jsonify(result)
            except Exception as e:
                log.exception(e)
                raise HTTP500InternalServerError(
                    title='Error converting to JSON',
                    description='Error converting to JSON from %s' % result)

