import time
#from bson import ObjectId
import hashlib
import app

log = app.get_logger('util')

def serialize(obj):
    if type(obj) in [list, set, tuple]:
        return [serialize(it) for it in obj]
    elif type(obj) == dict:
        for k, v in obj.iteritems():
            obj[k] = serialize(v)
        return obj
    elif type(obj) == '':#ObjectId:
        return str(obj)
    else:
        return obj


def deserialize(obj):
    if type(obj) is list:
        return [deserialize(it) for it in obj]
    elif type(obj) == dict:
        for k, v in obj.iteritems():
            if k == '_id':
                obj[k] = ''#ObjectId(obj[k])
            else:
                obj[k] = deserialize(obj[k])
        return obj
    else:
        return obj

def timestamp():
    return time.time() * 1000

def to_numeric(s):
    if s == '':
        return 0.0
    return float(s)

def is_numeric(s):
    try:
        to_numeric(s)
        return True
    except ValueError:
        return False

def to_boolean(s):
    s = s.lower()
    if s in ['true', 't', 'yes', 'y', '1']:
        return True
    if s in ['false', 'f', 'no', 'n', '0', '']:
        return False
    raise ValueError

def is_boolean(s):
    try:
        to_boolean(s)
        return True
    except ValueError:
        return False

def compute_query_list_hash(search_terms):
    query_terms_sorted = sorted(search_terms.split(','))
    query_terms_sorted_string = ''.join(query_terms_sorted)
    h = hashlib.new('ripemd160')
    h.update(query_terms_sorted_string)
    computed_hash = h.hexdigest()
    return computed_hash

