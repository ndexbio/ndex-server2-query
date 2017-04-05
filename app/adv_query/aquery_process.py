import argparse
import app
import json
import sys
import ndex.networkn as networkn
import time
import ndex.client as nc

def process_advanced_query(networkId, size, request, user, password):
    host = 'http://dev2.ndexbio.org'

    nc1 = nc.Ndex(host, user, password)
    response = nc1.get_network_as_cx_stream(networkId)

    cx = response.json()
    ndex_g = networkn.NdexGraph(cx)

    edge_ids_to_remove = []

    edge_filters = get_edge_filters(request)
    mode, node_filters = get_node_filters(request)

    if 'edgeLimit' in request:
        edge_limit = request['edgeLimit']
    else:
        edge_limit = 1500

    no_of_edges_to_keep = 0


    for edge_id, node_ids in iteritems(ndex_g.edgemap):

        source_node_id, target_node_id = node_ids
        edge = ndex_g[source_node_id][target_node_id][edge_id]

        source_node = ndex_g.node[source_node_id]
        target_node = ndex_g.node[target_node_id]

        if keep_edge(edge, edge_filters, node_filters, mode, source_node, target_node):
            no_of_edges_to_keep += 1

            if (no_of_edges_to_keep > edge_limit):
                # the resulting network is too big -- pass for now, but probably return empty set to the caller
                pass
        else:
            edge_ids_to_remove.append(edge_id)


    for edge_id in edge_ids_to_remove:
        ndex_g.remove_edge_by_id(edge_id)

    ndex_g.remove_orphan_nodes()

    add_advanced_query_criteria_to_properties(ndex_g, edge_filters, mode, node_filters)

    #nc1.save_new_network(ndex_g.to_cx())

    return ndex_g

def process_advanced_query_from_file_repo(ndex_g, size, request):
    edge_ids_to_remove = []

    edge_filters = get_edge_filters(request)
    mode, node_filters = get_node_filters(request)

    if 'edgeLimit' in request:
        edge_limit = request['edgeLimit']
    else:
        edge_limit = 1500

    no_of_edges_to_keep = 0

    for edge_id, node_ids in iteritems(ndex_g.edgemap):

        source_node_id, target_node_id = node_ids
        edge = ndex_g[source_node_id][target_node_id][edge_id]

        source_node = ndex_g.node[source_node_id]
        target_node = ndex_g.node[target_node_id]

        if keep_edge(edge, edge_filters, node_filters, mode, source_node, target_node):
            no_of_edges_to_keep += 1

            if (no_of_edges_to_keep > edge_limit):
                raise Exception({"message": "Too many edges returned.  Please increase filtering"})
                # the resulting network is too big -- pass for now, but probably return empty set to the caller
                # pass
        else:
            edge_ids_to_remove.append(edge_id)

    for edge_id in edge_ids_to_remove:
        ndex_g.remove_edge_by_id(edge_id)

    ndex_g.remove_orphan_nodes()

    add_advanced_query_criteria_to_properties(ndex_g, edge_filters, mode, node_filters)

    return ndex_g

def keep_edge(edge, edge_filters, node_filters, mode, source_node, target_node):

    if edge_filters:
        if not edge_satisfies_edge_query_criteria(edge, edge_filters):
            return False

    if node_filters:
        if not edge_satisfies_node_query_criteria(edge, node_filters, mode, source_node, target_node):
            return False

    return True



def edge_satisfies_edge_query_criteria(edge, edge_filters):

    for key in edge_filters:
        if key in edge:
            if edge[key].upper() in edge_filters[key]:
                return True

    return False


def edge_satisfies_node_query_criteria(edge, node_filters, mode, source_node, target_node):

    # handle an empty node_filter
    if node_filters.get("nodeFilter") is not None:
        if node_filters["nodeFilter"].get("propertySpecifications") is not None:
            if len(node_filters["nodeFilter"]["propertySpecifications"]) < 1:
                return True

    # value of mode is one of ["Source", "Target", "Both", "Either"]
    if mode == 'Source':
        if compare_node_attributes_to_query_criteria(source_node, node_filters):
            return True
        else:
            return False

    if mode == 'Target':
        if compare_node_attributes_to_query_criteria(target_node, node_filters):
            return True
        else:
            return False

    if mode == 'Either':
        if compare_node_attributes_to_query_criteria(target_node, node_filters):
            return True
        else:
            if compare_node_attributes_to_query_criteria(source_node, node_filters):
                return True
            else:
                return False

    if mode == 'Both':
        if compare_node_attributes_to_query_criteria(target_node, node_filters):
            if compare_node_attributes_to_query_criteria(source_node, node_filters):
                return True

    return False


def compare_node_attributes_to_query_criteria(node, node_filters):

    for key in node_filters:
        if key in node:
            if node[key].upper() in node_filters[key]:
                return True

    return False



def add_advanced_query_criteria_to_properties(ndex_g, edge_filters, mode, node_filters):

    if edge_filters:
        for key in edge_filters:
            if key == 'interaction':
                ndex_g.graph['aq:edge:interaction'] = edge_filters['interaction']
            else:
                ndex_g.graph['aq:edge:' + key] = edge_filters[key]

    if node_filters:
        if mode:
            if mode.startswith('Both'):
                mode = 'Both source and target'
            elif mode.startswith('Either'):
                mode = 'Either source or target'

            ndex_g.graph['aq:mode'] = mode

        for key in node_filters:
            if key == "ndex:name":
                ndex_g.graph['aq:node:name'] = node_filters["ndex:name"]
            else:
                ndex_g.graph['aq:node:' + key] = str(node_filters[key])

    return


def get_edge_filters(request):

    edge_filter = []

    if 'edgeFilter' not in request.keys():
        return edge_filter

    if request.get('edgeFilter') is None:
        return edge_filter

    if 'propertySpecifications' in request['edgeFilter']:
        request_edge_filter = request['edgeFilter']['propertySpecifications']

        if request_edge_filter:
            edge_filter = {}

        for filter in request_edge_filter:
            keys = filter.keys()
            if (('name' in keys) and ('value' in keys)):
                if (filter['name'] == 'ndex:interaction'):
                    if 'interaction' not in edge_filter:
                        edge_filter['interaction'] = []
                    edge_filter['interaction'].append(filter['value'].upper())
                else:
                    if filter['name'] not in edge_filter:
                        edge_filter[filter['name']] = []
                    edge_filter[filter['name']].append(filter['value'].upper())

    return edge_filter


def get_node_filters(request):
    node_filter = {"nodeFilter": {"propertySpecifications": [],"mode": "Source"}}
    mode = "Source"

    if 'nodeFilter' not in request.keys():
        return mode, node_filter

    if request.get('nodeFilter') is None:
        return node_filter

    if 'propertySpecifications' in request['nodeFilter']:
        request_node_filter = request['nodeFilter']['propertySpecifications']

        if request_node_filter:
            node_filter = {}

        if request['nodeFilter']['mode']:
            mode = request['nodeFilter']['mode']

        for filter in request_node_filter:
            keys = filter.keys()
            if (('name' in keys) and ('value' in keys)):
                if (filter['name'] == 'ndex:name'):
                    if 'name' not in node_filter:
                        node_filter['name'] = []
                    node_filter['name'].append(filter['value'].upper())

                else:
                    if filter['name'] not in node_filter:
                        node_filter[filter['name']] = []
                    node_filter[filter['name']].append(filter['value'].upper())

    return mode, node_filter

def iteritems(d):
    'Factor-out Py2-to-3 differences in dictionary item iterator methods'
    try:
        return d.iteritems()
    except AttributeError:
        return d.items()


