import os
import hashlib
from wand.image import Image

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

@middleware
def config_middleware(app, environ, start_response):
    environ['IMAGE_ROOT'] = '/opt/site/images'
    environ['CACHE_ROOT'] = '/opt/site/cache'
    return app(environ, start_response)

def NOT_FOUND(environ, start_response):
    body = b'Not Found'
    headers = [('Content-type', 'text/plain')]
    start_response('404 NOT FOUND', headers)
    return [body]

def FILE_RESPONSE(environ, path, block_size=4096):
    filelike = open(path, 'rb')
    if 'wsgi.file_wrapper' in environ:
        return environ['wsgi.file_wrapper'](filelike, block_size)
    else:
        return iter(lambda: filelike.read(block_size), '')

def GET_image(environ):
    if not (environ['REQUEST_METHOD'] == 'GET' 
            and environ['PATH_INFO'].startswith('/image/')):
        return None

    def handler(environ, start_response):
        image_root = environ['IMAGE_ROOT']
        cache_root = environ['CACHE_ROOT']

        parts = environ['PATH_INFO'][1:].split('/', 3)
        
        if len(parts) == 2:
            size = (400, 400)
            image_path = os.path.join(image_root, parts[1])
        else:
            size = [int(x) for x in parts[1].split('x')]
            image_path = os.path.join(image_root, parts[2])

        if not os.path.exists(image_path):
            return NOT_FOUND(environ, start_response)

        # Figure out if image is cached
        m = hashlib.sha256()
        m.update(image_path.encode('utf-8'))
        m.update(f'scale:{size[0]}x{size[1]}'.encode('utf-8'))
        cache_path = os.path.join(cache_root, m.hexdigest())

        if not os.path.exists(cache_path):
            # Write out cached
            with open(image_path, 'rb') as f:
                with Image(file=f) as img:
                    img.sample(size[0], size[1])
                    img.save(filename=cache_path)

        headers = [('Content-type', 'image/jpg')]
        start_response('200 OK', headers)
        return FILE_RESPONSE(environ, cache_path)
    return handler


@with_middleware([
    config_middleware
])
def application(environ, start_response):
    routes = [
        GET_image
    ]
    for route in routes:
        handler = route(environ)
        if handler is not None:
            return handler(environ, start_response)

    return NOT_FOUND(environ, start_response)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    with make_server('', 8000, application) as httpd:
        print("Serving on port 8000...")
        httpd.serve_forever()

