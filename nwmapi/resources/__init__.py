import logging

log = logging.getLogger(__name__)


class BaseHandler(object):
    def on_options(self, req, resp):
        resp.http204nocontent(resp)
