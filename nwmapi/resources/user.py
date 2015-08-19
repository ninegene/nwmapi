import falcon


class UserResource:

    def on_get(self, req, resp):
        raise falcon.HTTPServiceUnavailable(
            'Service unavailable',
            'Fetch data failed',
            30)

