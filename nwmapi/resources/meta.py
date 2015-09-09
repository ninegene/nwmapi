from collections import OrderedDict
import logging

from nwmapi.models.user import User
from nwmapi.resources import BaseHandler

log = logging.getLogger(__name__)

class MetaListResource(BaseHandler):
    __url__ = '/meta'

    def on_get(self, req, resp):
        results = OrderedDict()
        results[User.__tablename__] = User.description()
        resp.http200ok(result=results)
