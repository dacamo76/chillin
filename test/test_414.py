from nose import tools
from werkzeug import test, wrappers

import chillin


class Resource_414(chillin.Resource):
    def uri_too_long(self, uri):
        print uri
        print len(uri)
        return len(uri) > 50

    def to_html(self):
        return "DUMMY TEXT"


def wsgi_app_decorator(func):
    @wrappers.Request.application
    def wrapped(request):
        return func(request)
    return wrapped


def dispatch(path):
    return chillin.dispatcher([chillin.resource_uri(path, Resource_414)])


def test_verbs():
    for verb in {'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'CONNECT', 'OPTIONS'}:
        for uri in {'/', '/short/'}:
            yield valid_uri, uri, verb
        for uri in {'/sdsdfjkfjsdkfjsdkghdsfjghdfjghdfjghdjsghjdsbsdjvb/', '/l/o/n/g/u/r/i/_/s/h/o/u/l/d/_/4/1/4/'}:
            yield invalid_uri, uri, verb


def valid_uri(uri, verb):
    check_status(path=uri, verb=verb, valid=True)


def invalid_uri(uri, verb):
    print "in not valid"
    check_status(path=uri, verb=verb, valid=False)


def check_status(path, verb, valid):
    env = test.EnvironBuilder(path=path, method=verb)
    app = wsgi_app_decorator(dispatch(path))
    c = test.Client(app, wrappers.BaseResponse)
    code = c.open(env).status_code
    if valid:
        tools.assert_not_equal(code, 414)
    else:
        tools.assert_equal(code, 414)
