import os
import hashlib
from wand.image import Image
from utils import file_response, not_found_handler

def ensure_valid_path(root, path):
    abs_root = os.path.abspath(root)
    abs_path = os.path.abspath(path)
    if not abs_path.startswith(abs_root):
        raise Exception("Invalid path")

def hash_path(root, hexdigest, rest=None):
    path = os.path.join(root, hexdigest[:2], hexdigest[2:])
    if rest:
        path = os.path.join(path, rest)
    ensure_valid_path(root, path)
    return path

def _get_image_extension(path):
    for ext in ['jpg', 'png', 'gif']:
        if os.path.exists(path + '.' + ext):
            return ext
    return ''

def get_image_path(root, id):
    path = hash_path(root, id) 
    return path +  "." +  _get_image_extension(path)

def transform_handler(environ, start_response):
    img_id = environ['ROUTE_PARAMS']['id']
    img_path = get_image_path(environ['IMAGE_ROOT'], img_id)

    if os.path.exists(img_path):
        headers = [('Content-type', 'image/' + ext)]
        start_response('200 OK', headers)
        return file_response(environ, img_path)
    else:
        return not_found_handler(environ, start_response)

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

def image_handler(environ, start_response):
    img_id = environ['ROUTE_PARAMS']['id']
    img_path = get_image_path(environ['IMAGE_ROOT'], img_id)
    ext = img_path.split('.')[-1]

    if os.path.exists(img_path):
        headers = [('Content-type', 'image/' + ext)]
        start_response('200 OK', headers)
        return file_response(environ, img_path)
    else:
        headers = [('Content-type', 'text/plain')]
        start_response('200 OK', headers)
        return img_path
        #return not_found_handler(environ, start_response)



    

