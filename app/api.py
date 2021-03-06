#!/usr/local/bin/python

import sys
import argparse
import bottle
import traceback
from bottle import route, default_app, request, parse_auth, HTTPResponse, response
import time
from app.adv_query import aquery_process
import app
from app.FileRepo import NDExFileRepository

bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024

api = default_app()

log = app.get_logger('api')

@bottle.get('/message/<message>')
def api_message(message):
    return 'Hi: ' + message

@bottle.get('/')
def home():
    return '<strong>Hello from NDEx Advanced Query Service!</strong>'

@bottle.get('/v1/network/<id>/query')
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

@route('/v1/network/<id>/query' , method=['OPTIONS','POST'] )
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

@route('/v1/network/<id>/query_old' , method=['OPTIONS','POST'] )
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

@route('/search/network/<networkId>/advancedquery' , method=['OPTIONS','POST'] )
def get_advanced_query_request(networkId):
    try:
        request_json = request.json
        if request_json.get('nodeFilter') is None:
            request_json['nodeFilter'] = {'propertySpecifications': [],'mode': 'Source'}

        if request_json.get('edgeFilter') is None:
            request_json['edgeFilter'] = {'propertySpecifications': []}

        size = request_json['edgeLimit'] if ('edgeLimit' in request_json) else 1500
        #auth = parse_auth(request.get_header('Authorization', ''))
        #print auth

        ndexFileRepository = NDExFileRepository(networkId, load_from_cx=True)

        return dict(data=ndexFileRepository.advanced_search(size, request_json))

        #return_network = aquery_process.process_advanced_query(networkId, size, request_json, auth[0], auth[1])

        #return dict(data=return_network.to_cx())
    except Exception as e:
        log.error(e.message)
        traceback.print_exc()
        return HTTPResponse(dict(message=e.message), status=500)

class EnableCors(object):
    name = 'enable_cors'
    api = 2

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, Authorization'

            if request.method != 'OPTIONS':
                return fn(*args, **kwargs)

        return _enable_cors

def main():
    status = 0
    parser = argparse.ArgumentParser()
    parser.add_argument('port', nargs='?', type=int, help='HTTP port', default=8072)
    args = parser.parse_args()

    print 'starting web server on port %s' % args.port
    print 'press control-c to quit'

    try:
        log.info('entering main loop')
        api.install(EnableCors())
        api.run(host='0.0.0.0', port=args.port)
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