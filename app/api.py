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

@api.get('/api/query/:id/:queryterms')
def api_mongo_get_id(id, queryterms):
    ndexFileRepository = NDExFileRepository(id)
    return dumps(ndexFileRepository.search_network(queryterms))

@api.post('/network/:networkId/asCX/query')
def api_mongo_get_id(networkId):
    search_parms = request.json

    print networkId
    if('searchString' in search_parms.keys()):
        ndexFileRepository = NDExFileRepository(networkId)
        return dumps(ndexFileRepository.search_network(search_parms['searchString']))
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