import json
import logging

import falcon

log = logging.getLogger(__name__)

class RequestResponseLogger(object):
    def process_request(self, req, resp):
        log.info('%s %s %s', req.protocol.upper(), req.method, req.relative_uri)

    def process_response(self, req, resp, resource):
        log.info('%s', resp.body)


class RequireJSON(object):
    def process_request(self, req, resp):
        if not req.client_accepts_json:
            log.error('RequireJSON: req.client_accepts_json is empty')
            raise falcon.HTTPNotAcceptable(
                'Unsupported response encoding',
                href='')

        if req.method in ('POST', 'PUT'):
            if 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType(
                    'Unsupported content type',
                    href='')


class JSONTranslator(object):
    def process_request(self, req, resp):
        # req.stream corresponds to the WSGI wsgi.input environ variable,
        # and allows you to read bytes form the request body
        #
        # See also: PEP 3333
        if req.content_length in (None, 0):
            # Nothing to do
            return

        body = req.stream.read()
        if not body:
            raise falcon.HTTPBadRequest('Empty request body',
                                        'A valid JSON document is required.')

        try:
            req.context['doc'] = json.loads(body.decode('utf-8'))

        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPBadRequest('Malformed JSON',
                                        'Could not decode the request body. '
                                        'The JSON was incorrect or not encoded as UTF-8')

    def process_response(self, req, resp, resource):
        if 'result' not in req.context:
            return

        resp.body = json.dumps(req.context['result'])
