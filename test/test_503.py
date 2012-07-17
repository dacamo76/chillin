from nose import tools
from werkzeug import test, wrappers

import chillin


class Resource_503(chillin.Resource):
    def available(self): return False


def wsgi_app_decorator(func):
    @wrappers.Request.application
    def wrapped(request):
        return func(request)
    return wrapped

def dispatch(path):
    return chillin.dispatcher([chillin.resource_uri(path, Resource_503)])

def test_verbs():
    for verb in {'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'CONNECT', 'OPTIONS'}:
        yield check_status, '/', verb


def check_status(path, verb):
    env = test.EnvironBuilder(path=path, method=verb)
    app = wsgi_app_decorator(dispatch(path))
    c = test.Client(app, wrappers.BaseResponse)
    tools.assert_equals(c.open(env).status_code, 503)
