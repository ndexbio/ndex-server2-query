import os
import app
import json
from bson.json_util import dumps
import networkx as nx
import time
import sys

#==================================
# TESTING CODE - NEED TO USE
# LOCAL PACKAGE OF NETWORKN
# INSTEAD OF PIP INSTALLED VERSION
#==================================
#sys.path.append('~/Development/Projects/ndex-python/ndex')
#from networkn import NdexGraph_alt
from ndex.networkn import NdexGraph
#from ndex.client import Ndex

class NDExFileRepository():
    '''Temporary class to retrieve network files'''
    def __init__(self, uuid, load_from_cx=False):
        self.aspect_list = ''
        self.uuid = uuid
        self.repo_directory = app.repo_directory
        self.aspect_map = {}
        self.ndex_gsmall = {}
        self.ndex_gsmall_searched = {}

        if(uuid is None):
            raise Exception('UID missing.  Please provide the network id')
        else:
            if(load_from_cx):
                self.load_full_network()
            else:
                #self.load_full_network_from_aspects()
                self.load_minimum_network_from_aspects()

            self.nodes = self.load_aspect('nodes')

            #self.edges = self.load_aspect(self.uuid, 'edges')

    #===============================
    # GET LIST OF ASPECTS FROM REPO
    #===============================
    '''Gets the aspects available for the specified network uid '''
    def get_aspects(self):
        read_this_directory = os.path.join(self.repo_directory,self.uuid,'aspects')
        if os.path.isdir(read_this_directory):
            return os.listdir(read_this_directory)
        else:
            return ['No aspects available']

    #==============================
    # LOAD ASPECT FROM REPO (JSON)
    #==============================
    '''Loads the given aspect for the specified network uid'''
    def load_aspect(self, aspect):
        #====================================
        # Check the cache. Load if necessary
        #====================================
        if((self.uuid in self.aspect_map) and (aspect in self.aspect_map[self.uuid])):
            return self.aspect_map[self.uuid][aspect]
        else:
            read_this_aspect = ''
            if(aspect == 'full_network'):
                read_this_aspect = os.path.join(self.repo_directory,self.uuid,self.uuid + '.cx')
            else:
                read_this_aspect = os.path.join(self.repo_directory,self.uuid,'aspects',aspect)

            with open(read_this_aspect, 'rt') as fid:
                data = json.load(fid)
                if(data is not None):
                    if(self.uuid not in self.aspect_map):
                        self.aspect_map[self.uuid] = {}

                    self.aspect_map[self.uuid][aspect] = data

                    fid.close()
                    return self.aspect_map[self.uuid][aspect]

        return []

    #===============================
    # DEPRECATED DON'T USE
    # LOAD FULL CX FROM REPO (JSON)
    #===============================
    '''Loads the full network for the specified network uid'''
    def load_full_network(self):
        network_cx =  self.load_aspect('full_network')
        ndex_gsmall = NdexGraph(network_cx)
        self.ndex_gsmall = ndex_gsmall

        return self.ndex_gsmall

    #=============================================
    # LOAD FULL CX FROM REPO USING ASPECTS (JSON)
    #=============================================
    '''Loads the full network for the specified network uid'''
    def load_full_network_from_aspects(self):
        available_aspects = self.get_aspects()
        ndex_gsmall = NdexGraph()

        # 'subNetworks', 'cyViews', 'metaData' First
        if('subNetworks' in available_aspects):
            aspect_cx = self.load_aspect('subNetworks')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'subNetworks')

        if('cyViews' in available_aspects):
            aspect_cx = self.load_aspect('cyViews')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'cyViews')

        if('metaData' in available_aspects):
            aspect_cx = self.load_aspect('metaData')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'metaData')

        # 'nodes', 'edges' Second
        if('nodes' in available_aspects):
            aspect_cx =  self.load_aspect('nodes')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'nodes')

        if('edges' in available_aspects):
            aspect_cx =  self.load_aspect('edges')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'edges')

        # 'networkAttributes'  'nodeAttributes' 'edgeAttributes' Third
        if('networkAttributes' in available_aspects):
            aspect_cx =  self.load_aspect('networkAttributes')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'networkAttributes')

        if('nodeAttributes' in available_aspects):
            aspect_cx =  self.load_aspect('nodeAttributes')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'nodeAttributes')

        if('edgeAttributes' in available_aspects):
            aspect_cx =  self.load_aspect('edgeAttributes')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'edgeAttributes')

        # 'cartesianLayout' and all others last
        if('cartesianLayout' in available_aspects):
            aspect_cx =  self.load_aspect('cartesianLayout')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'cartesianLayout')

        self.ndex_gsmall = ndex_gsmall
        return ndex_gsmall

    #================================================
    # LOAD MINIMUM CX FROM REPO USING ASPECTS (JSON)
    #================================================
    '''Loads the minimum network for the specified network uid'''
    def load_minimum_network_from_aspects(self):
        available_aspects = self.get_aspects()
        ndex_gsmall = NdexGraph()

        # 'subNetworks', 'cyViews', 'metaData' First
        if('subNetworks' in available_aspects):
            aspect_cx = self.load_aspect('subNetworks')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'subNetworks')

        if('cyViews' in available_aspects):
            aspect_cx = self.load_aspect('cyViews')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'cyViews')

        if('metaData' in available_aspects):
            aspect_cx = self.load_aspect('metaData')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'metaData')

        # 'nodes', 'edges' Second
        if('nodes' in available_aspects):
            aspect_cx =  self.load_aspect('nodes')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'nodes')

        if('edges' in available_aspects):
            aspect_cx =  self.load_aspect('edges')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'edges')

        self.ndex_gsmall = ndex_gsmall
        return ndex_gsmall

    def get_ndex_gsmall(self):
        return self.ndex_gsmall

    #=====================================
    # SEARCH NETWORK FOR 1-STEP NEIGHBORS
    #=====================================
    '''returns the found nodes and their 1-step neighbors'''
    def search_network(self, search_terms, depth):
        #print ndexFileRepository.get_nodes_and_edges().edges()
        search_terms_array = [self.get_node_id_by_value(sn) for sn in search_terms.split(',')]

        aspect_list = self.get_aspects()

        #ndex_gsmall = self.load_full_network()
        #cx_version = self.ndex_gsmall.to_cx()

        n = self.ndex_gsmall.nodes()
        for i in range(depth):
            subgraph_nodes = []
            for term_id in search_terms_array:
                #term_id = self.get_node_id_by_value(term)
                if(term_id in n):
                    subgraph_nodes.append(term_id)
                    add_these_nodes = self.ndex_gsmall.neighbors(term_id)
                    for add_node in add_these_nodes:
                        if(add_node not in subgraph_nodes):
                            subgraph_nodes.append(add_node)

            search_terms_array = subgraph_nodes

        filtered_edge_ids = self.get_filtered_edge_ids(subgraph_nodes)

        ndex_gsmall_sub = self.ndex_gsmall.subgraph(subgraph_nodes)

        sub_nodes = ndex_gsmall_sub.nodes()
        remove_these_nodes = []
        keep_these_nodes = []
        for full_node in self.ndex_gsmall.nodes():
            if(full_node not in sub_nodes):
                remove_these_nodes.append(full_node)
            else:
                keep_these_nodes.append(full_node)

        #print '- Get deep copy'
        #start_time = time.time()
        self.ndex_gsmall_searched = self.ndex_gsmall.copy()
        #print str(start_time - time.time())

        self.ndex_gsmall_searched.remove_nodes_from(remove_these_nodes)

        #==========================================
        # Add all other aspects to the subnetwork
        #==========================================

        start_time = time.time()
        if('nodeAttributes' in aspect_list):
            node_attributes_cx =  self.load_aspect('nodeAttributes')
            for nodeAttribute in node_attributes_cx:
                id = nodeAttribute['po']
                name = nodeAttribute['n']
                # special: ignore selected
                if name == 'selected':
                    continue
                value = nodeAttribute['v']
                if 'd' in nodeAttribute:
                    d = nodeAttribute['d']
                    if d == 'boolean':
                        value = value.lower() == 'true'
                if 's' in nodeAttribute or name not in self.node[id]:
                    self.node[id][name] = value

        if('edgeAttributes' in aspect_list):
            edge_attributes_cx =  self.load_aspect('edgeAttributes')
            for edgeAttribute in edge_attributes_cx:
                id = edgeAttribute['po']
                if(id in filtered_edge_ids):
    #                s, t = self.edgemap[id]
                    name = edgeAttribute['n']
                    # special: ignore selected and shared_name columns
                    if name == 'selected' or name == 'shared name':
                        continue
                    value = edgeAttribute['v']
                    if 'd' in edgeAttribute:
                        d = edgeAttribute['d']
                        if d == 'boolean':
                            value = value.lower() == 'true'
    #                if 's' in edgeAttribute or name not in self[s][t][id]:
    #                    self[s][t][id][name] = value
                    #if(id in)
                    #print 'id,name,value: ' + str(id) + ' ' + str(name) + ' ' + str(value)
                    self.ndex_gsmall_searched.set_edge_attribute(id,name,value)

        print '- add attributes ' + str(time.time() - start_time)

        #ndex_gsmall_sub.write_to('../../cx/' + self.uuid + '_manual.cx')
        print 'edges: ' + str(len(self.ndex_gsmall_searched.edges()))

        return self.ndex_gsmall_searched.to_cx()

    def get_filtered_edge_ids(self, n_id_list):
 #       self_0 = self.ndex_gsmall.get_edge_id_by_source_target(None, None)
 #       edges_iter_list = self.ndex_gsmall.edges_iter(n_id_list)

        #edge_keys = {key: (s, t) for s, t, key in self.ndex_gsmall.edges_iter(n_id_list, keys=True)}
#        edge_ids = [key for s, t, key in self.ndex_gsmall.edges_iter(n_id_list, keys=True)]

#        for edge_id, s_t in edge_keys.items():
#            if s_t == (1, 355):
#                print 'Found 1, 355 id: ' + str(edge_id)

#        print 'Edge 1, 14 is: ' + str(self.ndex_gsmall.get_edge_data(1, 14))

#        for e_i_item in edges_iter_list:
#            print e_i_item

#        print n_id_list
#        e = self.ndex_gsmall.edges()

#        return_edges = []
#        for e_item in e:
#            if(e_item[0] in n_id_list and e_item[1] in n_id_list):
#                return_edges.append(e_item)
#        print 'Filtered Edges'
#        print dumps(return_edges)
#        return return_edges
        #print  [(s, t, key) for s, t, key in self.ndex_gsmall.edges_iter(n_id_list, keys=True) if s in n_id_list and t in n_id_list]

        return [key for s, t, key in self.ndex_gsmall.edges_iter(n_id_list, keys=True) if s in n_id_list and t in n_id_list]


    def get_nodes_and_edges(self):
        nodes = self.load_aspect('nodes')
        edges = self.load_aspect('edges')
        mainG = nx.Graph()
        for edge in edges:
            if(edge['i'] == 'interacts_with'):
                mainG.add_edge(self.get_node_value_by_id(edge['s']), self.get_node_value_by_id(edge['t']))

        return mainG

    def get_nodes_and_edges_from_cx(self, network_uid):
        nodes = self.load_aspect('nodes')
        edges = self.load_aspect('edges')
        mainG = nx.Graph()
        for edge in edges:
            if(edge['i'] == 'interacts_with'):
                mainG.add_edge(self.get_node_value_by_id(edge['s']), self.get_node_value_by_id(edge['t']))

        return mainG

    def get_node_value_by_id(self, uid):
        item = next((x for x in self.nodes if x['@id'] == uid), None)
        if(item is not None):
            if('n' in item):
                return item['n']
            else:
                return None
        else:
            return None

    def get_node_id_by_value(self, value):
        item = next((x for x in self.nodes if x['n'] == value), None)
        if(item is not None):
            if('@id' in item):
                return item['@id']
            else:
                return None
        else:
            return None

    def convert_aspect_to_networkx(self, network_uid, aspect):
        convert_this_aspect = {}
        #================================================
        # Check cache for the aspect.  Load if necessary
        #================================================
        if(self.uuid not in self.aspect_map):
            convert_this_aspect = self.load_aspect(aspect)
        else:
            if(aspect not in self.aspect_map[network_uid]):
                convert_this_aspect = self.load_aspect(aspect)
            else:
                convert_this_aspect = self.aspect_map[self.uuid][aspect]



