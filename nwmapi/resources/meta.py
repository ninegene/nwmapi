from collections import OrderedDict
from nwmapi.resources import BaseHandler


class MetaListResource(BaseHandler):
    def on_get(self, req, resp):
        results = OrderedDict()
        resp.http200ok(resp, result=results)