import logging

from nwmapi.httpstatus import send_http204_nocontent

log = logging.getLogger(__name__)


class BaseHandler(object):
    def on_options(self, req, resp):
        send_http204_nocontent(req, resp)
