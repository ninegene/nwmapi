import logging
import json
import falcon

from nwmapi.httpstatus import HTTP400BadRequest, HTTP406NotAcceptable, HTTP415UnsupportedMediaType
from nwmapi.models import get_dbsession
from sqlalchemy.exc import SQLAlchemyError

log = logging.getLogger(__name__)


class DBTransaction(object):
    def process_request(self, req, resp):
        log_debug(req, 'DBTransaction: before request')
        req.dbsession = get_dbsession()

    def process_response(self, req, resp, resource):
        log_debug(req, 'DBTransaction: after response')
        session = req.dbsession
        try:
            session.commit()
        except SQLAlchemyError as e:
            log.exception(e)
            session.rollback()
            raise
        finally:
            session.close()


class RequireJSON(object):
    def process_request(self, req, resp):
        log_debug(req, 'RequireJSON: before request')
        if not req.client_accepts_json:
            raise HTTP406NotAcceptable('Unsupported response encoding', href='https://url/to/docs')

        if req.method in ('POST', 'PUT'):
            if not req.content_type or 'application/json' not in req.content_type:
                raise HTTP415UnsupportedMediaType('Unsupported content type', href='https://url/to/docs')


class Request(falcon.Request):
    """Override falcon.Request to provide 'json' attribute on request object"""
    def __init__(self, env, options=None):
        super(Request, self).__init__(env, options)
        self.json = None


class JSONBodyTranslator(object):
    def process_request(self, req, resp):
        log_debug(req, 'JSONBodyTranslator: before request')
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
            req.json = json.loads(body)
        # except (ValueError, UnicodeDecodeError):
        except Exception as e:
            log.exception(e)
            raise HTTP400BadRequest(
                title='Malformed JSON',
                description='Could not decode the request body. '
                            'The JSON was incorrect or not encoded as UTF-8')



def log_debug(req, msg):
    log.debug('%s %s %s %s', msg, req.protocol.upper(), req.method, req.relative_uri)
