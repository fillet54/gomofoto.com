
def not_found_handler(environ, start_response):
    body = b'Not Found'
    headers = [('Content-type', 'text/plain')]
    start_response('404 NOT FOUND', headers)
    return [body]

def file_response(environ, path, block_size=4096):
    filelike = open(path, 'rb')
    if 'wsgi.file_wrapper' in environ:
        return environ['wsgi.file_wrapper'](filelike, block_size)
    else:
        return iter(lambda: filelike.read(block_size), '')

