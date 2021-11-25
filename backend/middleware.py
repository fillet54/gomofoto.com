
def middleware(f):
    def inner(app):
        def inner_app(environ, start_response):
            return f(app, environ, start_response)
        return inner_app
    return inner

def with_middleware(middlewares):
    def inner_decorator(f):
        for middleware in middlewares:
            f = middleware(f)
        return f
    return inner_decorator


def config_middleware(config):
    @middleware
    def inner_middleware(app, environ, start_response):
        environ.update(config)
        return app(environ, start_response)
    return inner_middleware
