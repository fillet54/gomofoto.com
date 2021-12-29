import re

def re_groups(matcher):
    for i in range(len(matcher.groups())):
        yield matcher.group(i+1)

def put_list(d, k, v):
    "Puts a key with a value into dictionary. If key already exists in dict, create list of values"
    cur = d.get(k, None)
    if cur:
        if isinstance(cur, list):
            cur.append(v)
            v = cur
        else:
            v = [cur, v] 
    d[k] = v

def put_keys_with_groups(groups, keys):
    d = dict()
    for (k, v) in zip(keys, groups):
        put_list(d, k, v)
    return d

def lex_1(src, clauses):
    """Scan one symbol from src and return a tuple of the symbol and remaining src"""
    for (regex, action) in clauses:
        matcher = re.match(regex, src)
        if matcher:
            if callable(action):
                action = action(matcher)
            return (action, src[matcher.end():])
    return None

def lex(src, clauses):
    """Return a list of symbols from string based on clauses. Clauses is a list of
       regex pattern and either replacement text or function that takes the match and 
       returns replacement text"""
    results = []
    while src != "":
        (result, src) = lex_1(src, clauses)
        results.append(result)
    return results

re_word    = r":(\w\w*)"
re_literal = r"(:[^\w*]|[^:*])+"

def word_group(matcher):
    return matcher.group(1)

def build_route_regex(path, regexs):
    def re_word_action(matcher):
        return "(%s)" % regexs.get(word_group(matcher), "[^/,;?]+")
    def re_literal_action(matcher):
        return re.escape(matcher.group())
    clauses = [(r"\*",     "(.*?)"),
               (re_word,    re_word_action),
               (re_literal, re_literal_action)]
    parts = lex(path, clauses)
    parts.append("\\Z")
    return "".join(parts)

def find_path_keys(path):
    clauses = [(r"\*", "*"),
               (re_word, word_group),
               (re_literal, None)]
    return filter(lambda x: x != None, lex(path, clauses))

class CompiledRoute(object):
    def __init__(self, source, regex, keys):
        self.source = source 
        self.regex = re.compile(regex)
        self.keys = keys

    def matches(self, environ):
        path_info = environ.get('PATH_INFO')
        matcher = self.regex.match(path_info)
        if matcher:
            return put_keys_with_groups(re_groups(matcher), self.keys)
        
        # Add trailing slash
        path_info = path_info + "/"
        matcher = self.regex.match(path_info)
        if matcher:
            return put_keys_with_groups(re_groups(matcher), self.keys)

        return None

    def __str__(self):
        return '<CompiledRoute: {}>'.format(self.regex)

def route_compile(path, regexs):
    regexs = regexs or dict()
    path_keys = find_path_keys(path)
    return CompiledRoute(path, 
                         build_route_regex(path, regexs), 
                         path_keys)

def method_matches (request, method):
    '''Determines if request method matches specified option
    TODO: Form post
    
    >>> method_matches({'REQUEST_METHOD': 'GET'}, 'GET')
    True
    >>> method_matches({'REQUEST_METHOD': 'HEAD'}, 'GET')
    True
    >>> method_matches({'REQUEST_METHOD': 'GET'}, 'POST')
    False
    '''
    if method in [None, 'ANY']:
        return True
    
    request_method = request.get('REQUEST_METHOD')

    if request_method == 'HEAD':
        return method in ['HEAD', 'GET']
    return request_method == method


def make_route(method, path, handler, regexs=None):
    route = route_compile(path, regexs)
    def route_matches(environ):
        if method_matches(environ, method):
            route_params = route.matches(environ)
            if route_params:
                environ['ROUTE_PARAMS'] = route_params
                return handler
    return route_matches

def ANY(path, handler, regexs=None):
    return make_route("ANY", path, handler, regexs)

def GET(path, handler, regexs=None):
    return make_route("GET", path, handler, regexs)

def POST(path, handler, regexs=None):
    return make_route("POST", path, handle, regexs)


if __name__ == '__main__':


    r = route_compile('/image/:id', None)

    print(r)

    m = r.regex.match('/image/asdfasdfasdfasf')
    print(m)

    p = r.matches(dict(PATH_INFO='/image/123ljjkalsdf234232', REQUEST_METHOD='GET'))
    print(p)

    rr = GET('/image/:id', 123)

    h = rr(dict(PATH_INFO='/image/123ljjkalsdf234232', REQUEST_METHOD='GET'))
    print(h)
