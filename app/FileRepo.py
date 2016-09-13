import os
import app
import json
from bson.json_util import dumps
import networkx as nx
from ndex.networkn import NdexGraph

class NDExFileRepository():
    '''Temporary class to retrieve network files'''
    def __init__(self, uuid):
        self.aspect_list = ''
        self.uuid = uuid
        self.repo_directory = app.repo_directory
        self.aspect_map = {}

        if(uuid is None):
            raise Exception('UID missing.  Please provide the network id')
        else:
            self.load_full_network()
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

        return None

    #===============================
    # LOAD FULL CX FROM REPO (JSON)
    #===============================
    '''Loads the full network for the specified network uid'''
    def load_full_network(self):
        network_cx =  self.load_aspect('full_network')
        ndex_gsmall = NdexGraph(network_cx)

        return ndex_gsmall

    #=====================================
    # SEARCH NETWORK FOR 1-STEP NEIGHBORS
    #=====================================
    '''returns the found nodes and their 1-step neighbors'''
    def search_network(self, search_terms):
        search_terms_array = search_terms.split(',')
        ndex_gsmall = self.load_full_network()

        n = ndex_gsmall.nodes()
        subgraph_nodes = []
        for term in search_terms_array:
            term_id = self.get_node_id_by_value(term)
            if(term_id in n):
                subgraph_nodes.append(term_id)
                add_these_nodes = ndex_gsmall.neighbors(term_id)
                for add_node in add_these_nodes:
                    subgraph_nodes.append(add_node)

        ndex_gsmall_sub = ndex_gsmall.subgraph(subgraph_nodes)

        #ndex_gsmall_sub.write_to('../../cx/' + self.uuid + '_manual.cx')

        return ndex_gsmall_sub.to_cx()

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



