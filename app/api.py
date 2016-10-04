#!/usr/local/bin/python

import sys
import pymongo
import argparse
from bson import ObjectId
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import bottle
from bottle import Bottle, redirect, static_file, request

bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024

import app
from app.util import serialize
from app.FileRepo import NDExFileRepository
from bson.json_util import dumps

api = Bottle()

log = app.get_logger('api')

@api.get('/v1/network/:id/query')
def api_query_get_by_id(id):
    #id = request.query.get('id')
    query_terms = request.query.get('terms')
    depth = request.query.get('depth')
    if(id is not None and query_terms is not None):
        ndexFileRepository = NDExFileRepository(id)
        return dumps(ndexFileRepository.search_network(query_terms, depth))
    else:
        return {'message': 'not found'}

@api.post('/v1/network/:id/query')
def api_query_get_by_id_post(id):
    search_parms = request.json

    search_depth = 1
    if('depth' in search_parms.keys()):
        search_depth = search_parms['depth']

    #if('searchString' in search_parms.keys() and 'uuid' in search_parms.keys()):
    if('searchString' in search_parms.keys()):
        if(len(id) < 1):
            return {'message': 'invalid uuid'}

        if(len(search_parms['searchString']) <= 2):
            return {'message': 'invalid search string'}

        ndexFileRepository = NDExFileRepository(id)

        return dumps(ndexFileRepository.search_network(search_parms['terms'],search_parms['depth']))
    else:
        return {'message': 'not found'}

# run the web server
def main():
    status = 0
    parser = argparse.ArgumentParser()
    parser.add_argument('port', nargs='?', type=int, help='HTTP port', default=80)
    args = parser.parse_args()

    print 'starting web server on port %s' % args.port
    print 'press control-c to quit'
    try:
        server = WSGIServer(('0.0.0.0', args.port), api, handler_class=WebSocketHandler)
        log.info('entering main loop')
        server.serve_forever()
    except KeyboardInterrupt:
        log.info('exiting main loop')
    except Exception as e:
        str = 'could not start web server: %s' % e
        log.error(str)
        print str
        status = 1

    log.info('exiting with status %d', status)
    return status

if __name__ == '__main__':
    sys.exit(main())