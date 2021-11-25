import logging

from router import ANY, GET, POST
from middleware import config_middleware, with_middleware
from utils import not_found_handler
from image import image_handler


@with_middleware([
    config_middleware({
        'IMAGE_ROOT': '/opt/site/images',
        'CACHE_ROOT': '/opt/site/cache'})
])
def application(environ, start_response):
    routes = [
        GET('/image/*', image_handler)
    ]
    for route in routes:
        handler = route(environ)
        if handler is not None:
            response = handler(environ, start_response)
            if response:
                return response

    return not_found_handler(environ, start_response)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    with make_server('', 8000, application) as httpd:
        logging.info("Serving on port 8000...")
        httpd.serve_forever()

