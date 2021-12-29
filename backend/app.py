import logging

from router import ANY, GET, POST
from middleware import config_middleware, with_middleware
from utils import not_found_handler
from image import image_handler

def make_app(routes, config):

    @with_middleware([
        config_middleware(config)
    ])
    def app(environ, start_response):
        for route in routes:
            handler = route(environ)
            if handler is not None:
                response = handler(environ, start_response)
                if response:
                    return response
    
        return not_found_handler(environ, start_response)
    return app

routes = [
    GET('/image/:id', image_handler),
]

config = {
    'IMAGE_ROOT': '/opt/site/images',
}

application = make_app(routes, config)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    with make_server('', 8000, application) as httpd:
        logging.info("Serving on port 8000...")
        httpd.serve_forever()

