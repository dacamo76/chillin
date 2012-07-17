from nose import tools
from werkzeug import test, wrappers

import chillin

KNOWN = {'GET', 'HEAD', 'HUH?'}

class Resource_501(chillin.Resource):
    def known_methods(self):
        return KNOWN

    def to_html(self):
        return "DUMMY TEXT"


def wsgi_app_decorator(func):
    @wrappers.Request.application
    def wrapped(request):
        return func(request)
    return wrapped

def dispatch(path):
    return chillin.dispatcher([chillin.resource_uri(path, Resource_501)])

def test_verbs():
    for verb in {'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'CONNECT', 'OPTIONS'}:
        yield check_status, '/', verb


def check_status(path, verb):
    env = test.EnvironBuilder(path=path, method=verb)
    app = wsgi_app_decorator(dispatch(path))
    c = test.Client(app, wrappers.BaseResponse)
    code = c.open(env).status_code
    if verb in KNOWN:
        tools.assert_not_equal(code, 501)
    else:
        tools.assert_equal(code, 501)
