from werkzeug import routing
from werkzeug import wrappers
from werkzeug import exceptions as ex


class Resource(object):

    def return_options(self):
        return wrappers.BaseResponse(response=None, status=200, headers=self.options())

    def __call__(self, req, **kwargs):
        if not self.available():
            ex.abort(503)
        if req.method not in self.known_methods():
            ex.abort(501)
        if self.uri_too_long(req.url):
            ex.abort(414)
        if req.method not in self.accepted_methods():
            ex.abort(405, valid_methods=self.accepted_methods())
        if self.malformed_request(req):
            ex.abort(400)
        if not self.authorized(req.authorization):
            ex.abort(401)
        if self.forbidden(req):
            ex.abort(403)
        if not self.valid_content_headers(req.headers):
            ex.abort(501)
        if not self.known_content_type(req.mimetype):
            ex.abort(415)
        if self.request_entity_too_large(req):
            ex.abort(413)

        if req.method == 'OPTIONS':
            return self.return_options()

        return wrappers.Response(self.to_html(), mimetype='text/html')
   
    def available(self):
        return True

    def known_methods(self):
        return {'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'CONNECT', 'OPTIONS'}

    def uri_too_long(self, uri):
        return False

    def accepted_methods(self):
        return {'GET', 'HEAD'}

    def malformed_request(self, req):
        return False

    def authorized(self, authorization):
        return True

    def forbidden(self, req):
        return False

    def valid_content_headers(self, headers):
        return True

    def known_content_type(self, content_type):
        return True

    def request_entity_too_large(self, length):
        return False

    def options(self):
        """Returns list of Header tuples that will appear in the response."""
        return set()

    def provided_media_types(self):
        [('text/html', to_html)]

    def provided_languages(self):
        return []

    def provided_charsets(self):
        return []

    def provided_encodings(self):
        return []

    def resource_exists(self):
        return True


def resource_uri(path, resource, **kwargs):
    resource = resource(**kwargs)
    return routing.Rule(path, endpoint=resource)


def dispatcher(mappings):
    def dispatch(req):
        urls = mappings.bind_to_environ(req.environ)
        return urls.dispatch(lambda e, v: e(req, **v), catch_http_exceptions=True)
    return dispatch

