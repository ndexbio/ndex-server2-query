#!/usr/local/bin/python

import sys
import argparse
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import bottle
from bottle import Bottle, redirect, static_file, request, abort, HTTPResponse, response
import time
import json
from app.adv_query import aquery_process

bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024

import app
from app.util import serialize
from app.FileRepo import NDExFileRepository
#from bson.json_util import dumps

api = Bottle()

log = app.get_logger('api')

@api.get('/message/:message')
def api_message(message):
    return 'Hi: ' + message

@api.get('/v1/network/:id/query')
def api_query_get_by_id(id):
    #id = request.query.get('id')
    query_terms = request.query.get('terms')
    depth = request.query.get('depth')
    if(id is not None and query_terms is not None):
        try:
            ndexFileRepository = NDExFileRepository(id)
            return dict(data=ndexFileRepository.search_network(query_terms, depth))
        except Exception as e:
            log.error(e.message)
    else:
        return {'message': 'not found'}

@api.post('/v1/network/:id/query')
def api_query_get_by_id_post(id):
    search_parms = request.json

    search_depth = 1
    if('depth' in search_parms.keys()):
        search_depth = search_parms['depth']

    if('terms' in search_parms.keys()):
        if(len(id) < 1):
            return HTTPResponse(dict(message='invalid network id'), status=500)

        if(len(search_parms['terms']) <= 2):
            return HTTPResponse(dict(message='invalid search string'), status=500)

        try:
            start_time = time.time()
            ndexFileRepository = NDExFileRepository(id, load_from_cx=True)
            app.get_logger('PERFORMANCE').warning('Build time: ' + str(time.time() - start_time))
            print search_parms['terms']

            return dict(data=ndexFileRepository.search_network_new(search_parms['terms'],search_parms['depth'], max_edges=1500))
        except Exception as e:
            if len(e.message) < 1:
                log.error(e.strerror)
                return HTTPResponse(dict(message=e.strerror), status=500)
            else:
                log.error(e.message)
                return HTTPResponse(dict(message=e.message), status=500)

    else:
        return {'message': 'not found'}


@api.post('/v1/network/:id/query_old')
def api_query_get_by_id_post(id):
    search_parms = request.json

    search_depth = 1
    if('depth' in search_parms.keys()):
        search_depth = search_parms['depth']

    if('terms' in search_parms.keys()):
        if(len(id) < 1):
            return HTTPResponse(dict(message='invalid network id'), status=500)

        if(len(search_parms['terms']) <= 2):
            return HTTPResponse(dict(message='invalid search string'), status=500)

        try:
            start_time = time.time()
            ndexFileRepository = NDExFileRepository(id)
            app.get_logger('PERFORMANCE').warning('Build time: ' + str(time.time() - start_time))

            return dict(data=ndexFileRepository.search_network(search_parms['terms'],search_parms['depth']))
        except Exception as e:
            log.error(e.message)
            return HTTPResponse(dict(message=e.message), status=500)

    else:
        return {'message': 'not found'}

# /search/network/{networkId}/query?size={limit}
@api.post('/search/network/:networkId/query')
def get_advanced_query_request(networkId):
    size = request.query.get("size")
    request_json = request.json # json.load(request.body)
    #print(json.dumps(request_json, indent=3, sort_keys=True))

    return_network = aquery_process.process_advanced_query(networkId, size, request_json)

    return dict(data=return_network.to_cx())



class EnableCors(object):
    name = 'enable_cors'
    api = 2

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

            if request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors

api.install(EnableCors())

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