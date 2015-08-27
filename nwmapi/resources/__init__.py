import logging

import falcon
from nwmapi.httpstatus import send_http204_nocontent
import re

log = logging.getLogger(__name__)


class BaseHandler(object):
    def on_options(self, req, resp):
        send_http204_nocontent(req, resp)


def _HTTPError_to_dict(self, obj_type=dict):
    """Returns a basic dictionary representing the error.

    This method can be useful when serializing the error to hash-like
    media types, such as YAML, JSON, and MessagePack.

    Args:
        obj_type: A dict-like type that will be used to store the
            error information (default ``dict``).

    Returns:
        A dictionary populated with the error's title, description, etc.

    """

    assert self.has_representation

    obj = obj_type()

    if self.status is not None:
        try:
            try:
                obj['status'] = int(re.findall(r'^\d+', self.status)[0])
            except:
                obj['status'] = int(self.status)
        except:
            obj['status'] = self.status

    if self.title is not None:
        obj['title'] = self.title

    if self.description is not None:
        obj['description'] = self.description

    if self.code is not None:
        obj['code'] = self.code

    if self.link is not None:
        obj['link'] = self.link

    return obj

# Monkey patch to_dict to include 'status' attribute
falcon.HTTPError.to_dict = _HTTPError_to_dict
