import os
import hashlib
from wand.image import Image
from utils import file_response

def image_handler(environ, start_response):
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
    return file_response(environ, cache_path)
