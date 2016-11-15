import os
import app
import json
#from bson.json_util import dumps
import networkx as nx
from networkx import Graph
import time
import sys
import pysolr
from pysolr import SolrError
from app import solr_url
from app import temp_append_path

#==================================
# TESTING CODE - NEED TO USE
# LOCAL PACKAGE OF NETWORKN
# INSTEAD OF PIP INSTALLED VERSION
#==================================
sys.path.append(app.temp_append_path)
from networkn import NdexGraph

#from ndex.networkn import NdexGraph
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
        self.metadata_dict = {}
        self.node = []
        self.searched_node_map = {}
        self.searched_edge_map = {}
        self.citation_map = {}
        self.supports_map = {}
        self.filtered_node_attributes_list = []
        self.filtered_edge_attributes_list = []
        self.filtered_function_terms_list = []
        self.filtered_citation_list = []
        self.filtered_node_citation_list = []
        self.filtered_edge_citation_list = []
        self.known_aspects = ['cartesianLayout','citations','cyViews','edgeAttributes','edgeCitations','edges',
                              'edgeSupports','functionTerms','metaData','networkAttributes','nodeAttributes',
                              'nodeCitations','nodes','nodeSupports','supports','subNetworks','reifiedEdges',
                              'cyVisualProperties','visualProperties']
        self.aspect_list = None

        if(uuid is None):
            raise Exception('UID missing.  Please provide the network id')
        else:
            if(load_from_cx):
                self.load_full_network()
            else:
                #self.load_full_network_from_aspects()
                try:
                    self.load_minimum_network_from_aspects()
                    self.load_minimum_undirected()
                except KeyError as ke:
                    raise KeyError(ke)

            #self.nodes = self.load_aspect('nodes')

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
            return None

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
                read_this_aspect = os.path.join(self.repo_directory,self.uuid, 'network.cx')#self.uuid + '.cx')
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
        self.nodes = self.load_aspect('nodes')
        ndex_gsmall = NdexGraph(network_cx)
        self.ndex_gsmall = ndex_gsmall
        self.aspect_list = self.get_aspects()

        return self.ndex_gsmall

    #================================================
    # LOAD MINIMUM CX FROM REPO USING ASPECTS (JSON)
    #================================================
    '''Loads the minimum network for the specified network uid'''
    def load_minimum_network_from_aspects(self):
        ''' Loads the basic network elements (nodes and edges).
        Used for querying where the returned network will be a subset of the
        full network and therefore only need the corresponding attributes and not all attributes

        :return: Network
        :rtype: Networkn
        '''
        available_aspects = self.get_aspects()

        if(available_aspects is None):
            raise Exception("Network not found")

        ndex_gsmall = NdexGraph()

        if('subNetworks' in available_aspects):
            aspect_cx = self.load_aspect('subNetworks')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'subNetworks')
        # subNetworks is added automatically in networkn. Thus we need to include it in the metadata
        self.metadata_dict['subNetworks'] = 0

        if('cyViews' in available_aspects):
            aspect_cx = self.load_aspect('cyViews')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'cyViews')
        # cyViews is added automatically in networkn. Thus we need to include it in the metadata
        self.metadata_dict['cyViews'] = 0

        if('metaData' in available_aspects):
            aspect_cx = self.load_aspect('metaData')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'metaData')

        if('nodes' in available_aspects):
            aspect_cx =  self.load_aspect('nodes')
            self.nodes = aspect_cx

            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'nodes')
                self.metadata_dict['nodes'] = 0
        else:
            raise Exception("No nodes found. Nodes are required in aspects")

        if('edges' in available_aspects):
            aspect_cx =  self.load_aspect('edges')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'edges')
                self.metadata_dict['edges'] = 0
        else:
            raise Exception("No edges found. Edges are required in aspects")

        self.ndex_gsmall = ndex_gsmall
        self.aspect_list = self.get_aspects()
        return ndex_gsmall

    #================================================
    # LOAD MINIMUM UNDIRECTED GRAPH
    #================================================
    def load_minimum_undirected(self):
        available_aspects = self.get_aspects()
        gsmall = Graph()

        if('edges' in available_aspects):
            aspect_cx =  self.load_aspect('edges')
            if(len(aspect_cx) > 0):
                for edge in aspect_cx:
                    id = edge['@id']
                    interaction = edge['i'] if 'i' in edge else None
                    s = edge['s']
                    t = edge['t']
                    if interaction:
                        gsmall.add_edge(s, t, key=id, interaction=interaction)
                    else:
                        gsmall.add_edge(s, t, key=id)
        else:
            raise KeyError("No edges found. Edges are required in aspects")

        self.gsmall = gsmall
        self.aspect_list = self.get_aspects()
        return gsmall

    #=============================================
    # LOAD FULL CX FROM REPO USING ASPECTS (JSON)
    #=============================================
    '''Loads the full network for the specified network uid'''
    def load_full_network_from_aspects(self):
        available_aspects = self.get_aspects()
        ndex_gsmall = NdexGraph()

        if('subNetworks' in available_aspects):
            aspect_cx = self.load_aspect('subNetworks')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'subNetworks')
                self.metadata_dict['subNetworks'] = 0

        if('cyViews' in available_aspects):
            aspect_cx = self.load_aspect('cyViews')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'cyViews')
                self.metadata_dict['cyViews'] = 0

        if('metaData' in available_aspects):
            aspect_cx = self.load_aspect('metaData')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'metaData')

        if('nodes' in available_aspects):
            aspect_cx =  self.load_aspect('nodes')
            self.nodes = aspect_cx
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'nodes')
                self.metadata_dict['nodes'] = 0
        else:
            raise KeyError("Nodes not an available aspect for this network")

        if('edges' in available_aspects):
            aspect_cx =  self.load_aspect('edges')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'edges')
                self.metadata_dict['edges'] = 0
        else:
            raise KeyError("Edges not an available aspect for this network")

        if('networkAttributes' in available_aspects):
            aspect_cx =  self.load_aspect('networkAttributes')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'networkAttributes')
                self.metadata_dict['networkAttributes'] = 0

        if('nodeAttributes' in available_aspects):
            aspect_cx =  self.load_aspect('nodeAttributes')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'nodeAttributes')
                self.metadata_dict['nodeAttributes'] = 0

        if('edgeAttributes' in available_aspects):
            aspect_cx =  self.load_aspect('edgeAttributes')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'edgeAttributes')
                self.metadata_dict['edgeAttributes'] = 0

        if('cartesianLayout' in available_aspects):
            aspect_cx =  self.load_aspect('cartesianLayout')
            if(len(aspect_cx) > 0):
                ndex_gsmall.create_from_aspects(aspect_cx, 'cartesianLayout')
                self.metadata_dict['cartesianLayout'] = 0

        self.ndex_gsmall = ndex_gsmall
        return ndex_gsmall

    def get_ndex_gsmall(self):
        return self.ndex_gsmall

    def knbrs(self, G, start, k):
        neighbors = {}
        nbrs = set(start)
        for l in range(k):
            nbrs = set((nbr for n in nbrs for nbr in G[n]))
            neighbors[l] = nbrs
        return nbrs

    def get_n_step_neighbors(self, n_step, search_terms):
        search_terms_dict = {k:0 for k in search_terms}
        n = self.gsmall.nodes()

        # Initialize
        for search_term_i in search_terms:
            if(search_terms_dict.get(search_term_i) is None):
                search_terms_dict[search_term_i] = 0

        temp_search_terms_array = search_terms
        n = self.gsmall.nodes()
        for i in range(n_step):
            start_time = time.time()
            temp_search_terms_array = []
            for k, v in search_terms_dict.iteritems():
                if(k in n):
                    add_these_nodes = self.gsmall.neighbors(k)
                    for add_node in add_these_nodes:
                        if(search_terms_dict.get(add_node) is None):
                            temp_search_terms_array.append(add_node)

            for search_term_i in temp_search_terms_array:
                if(search_terms_dict.get(search_term_i) is None):
                    search_terms_dict[search_term_i] = 0
            app.get_logger('PERFORMANCE').warning('N-step (' + str(i) + '): ' + str(time.time() - start_time))
            print 'N-step (' + str(i) + '): ' + str(time.time() - start_time)

        return [k for k,v in search_terms_dict.iteritems()]

    #=====================================
    # SEARCH NETWORK FOR n-STEP NEIGHBORS
    #=====================================
    '''returns the found nodes and their n-step neighbors'''
    def search_network(self, search_terms, depth=1):
        if(type(depth) is not int):
            raise Exception("Depth must be an integer")

        start_time = time.time()
        solr = pysolr.Solr(solr_url + self.uuid + '/', timeout=10)

        try:
            results = solr.search(search_terms, rows=10000)
            search_terms_array = [int(n['id']) for n in results.docs]
            #print 'Initial Search Terms: ' + dumps(search_terms_array)
            app.get_logger('PERFORMANCE').warning('SOLR time: ' + str(time.time() - start_time))
            print 'SOLR time: ' + str(time.time() - start_time)

            #==========================================
            # GET THE NODES in the n-step neighborhood
            #==========================================
            subgraph_nodes = self.get_n_step_neighbors(depth, search_terms_array)

            start_time = time.time()
            self.ndex_gsmall_searched = self.ndex_gsmall.subgraph_new(subgraph_nodes)
            app.get_logger('PERFORMANCE').warning('Subgraph time: ' + str(time.time() - start_time))
            print 'Subgraph time: ' + str(time.time() - start_time)

            #Free up the temp undirected graph
            self.gsmall = None

            self.searched_node_map = {id: 0 for id in self.ndex_gsmall_searched.nodes()}
            self.searched_edge_map = self.ndex_gsmall_searched.edgemap

            start_time = time.time()

            #======================
            # NODE ATTRIBUTES
            #======================
            self.load_filtered_node_attributes()

            #======================
            # EDGE ATTRIBUTES
            #======================
            self.load_filtered_edge_attributes()

            #======================
            # FUNCTION TERMS
            #======================
            self.load_filtered_function_terms()

            #======================================
            # SUPPORTS (MUST RUN BEFORE CITATIONS)
            #======================================
            self.load_filtered_support()

            #======================
            # CITATIONS
            #======================
            self.load_filtered_citations()

            #======================
            # REIFIED EDGES
            #======================
            self.load_reified_edges()

            #======================
            # CY VISUAL PROPERTIES
            #======================
            self.load_cy_visual_properties()

            #======================
            # NETWORK ATTRIBUTES
            #======================
            self.load_network_attributes()

            #======================
            # OPAQUE ASPECTS
            # Update: ***
            # Opaque aspects are
            # not needed for
            # query
            #======================
            #for aspect_type in self.aspect_list:
            #    if(aspect_type not in self.known_aspects):
            #        self.metadata_dict[aspect_type] = 0
            #        load_this_opaque_aspect =  self.load_aspect(aspect_type)
            #        self.ndex_gsmall_searched.create_from_aspects(load_this_opaque_aspect, aspect_type)

            app.get_logger('PERFORMANCE').warning('Assemble query network: ' + str(time.time() - start_time))
            print 'Assemble query network: ' + str(time.time() - start_time)

            self.ndex_gsmall_searched.add_status({'error' : '','success' : True})

            return self.ndex_gsmall_searched.to_cx(md_dict=self.metadata_dict)

        except SolrError as se:
            if('404' in se.message):
                app.get_logger('SOLR').warning('Network not found ' + self.uuid + ' on ' + solr_url + ' server.')
                raise Exception("Network not found (SOLR)")
            #raise SolrError(se)

        return None

    def load_reified_edges(self):
        if('reifiedEdges' in self.aspect_list):
            self.metadata_dict['reifiedEdges'] = 0
            reified_edges_cx =  self.load_aspect('reifiedEdges')
            filtered_reified_edges = []
            for reified_edge in reified_edges_cx:
                node = reified_edge['node']
                edge = reified_edge['edge']
                if(self.searched_node_map.get(node) is not None and self.ndex_gsmall_searched.edgemap.get(edge) is not None):
                    filtered_reified_edges.append(reified_edge)

            if(len(filtered_reified_edges) > 0):
                self.ndex_gsmall_searched.create_from_aspects(filtered_reified_edges, 'reifiedEdges')

    def load_cy_visual_properties(self):
        if('cyVisualProperties' in self.aspect_list):
            self.metadata_dict['cyVisualProperties'] = 0
            cy_visual_properties_cx =  self.load_aspect('cyVisualProperties')
            self.ndex_gsmall_searched.create_from_aspects(cy_visual_properties_cx, 'cyVisualProperties')

        if('visualProperties' in self.aspect_list):
            self.metadata_dict['visualProperties'] = 0
            cy_visual_properties_cx =  self.load_aspect('visualProperties')
            self.ndex_gsmall_searched.create_from_aspects(cy_visual_properties_cx, 'visualProperties')

    def load_network_attributes(self):
        if('networkAttributes' in self.aspect_list):
            self.metadata_dict['networkAttributes'] = 0
            network_attributes_cx =  self.load_aspect('networkAttributes')
            # Blank out description property.
            # Description is only applicable to the parent network
            for n_a_cx_item in network_attributes_cx:
                if n_a_cx_item.get('n') == 'description':
                    n_a_cx_item['v'] = ''
            self.ndex_gsmall_searched.create_from_aspects(network_attributes_cx, 'networkAttributes')

    def load_filtered_node_attributes(self):
        if('nodeAttributes' in self.aspect_list):
            self.metadata_dict['networkAttributes'] = 0
            node_attributes_cx =  self.load_aspect('nodeAttributes')
            for nodeAttribute in node_attributes_cx:
                id = nodeAttribute['po']

                if(self.searched_node_map.get(id) is not None):
                    name = nodeAttribute['n']
                    # special: ignore selected
                    if name == 'selected':
                        continue
                    value = nodeAttribute['v']
                    if 'd' in nodeAttribute:
                        d = nodeAttribute['d']
                        if d == 'boolean':
                            value = value.lower() == 'true'
                    if 's' in nodeAttribute or name not in self.ndex_gsmall_searched.node[id]:
                        self.ndex_gsmall_searched.graph[name] = value
                        self.ndex_gsmall_searched.set_node_attribute(id, name, value)

        node_attributes_cx = None

    def load_filtered_edge_attributes(self):
        if('edgeAttributes' in self.aspect_list):
            self.metadata_dict['edgeAttributes'] = 0
            edge_attributes_cx =  self.load_aspect('edgeAttributes')
            for edgeAttribute in edge_attributes_cx:
                id = edgeAttribute['po']
                #if(id in filtered_edge_ids):
                #edgemap_id = self.ndex_gsmall_searched.edgemap[id]
                #print 'edgemap_id: ' + str(id) + ' s, t: ' + dumps(edgemap_id)
                if(self.ndex_gsmall_searched.edgemap.get(id) is not None):

                    name = edgeAttribute['n']
                    # special: ignore selected and shared_name columns
                    if name == 'selected' or name == 'shared name':
                        continue
                    value = edgeAttribute['v']
                    if 'd' in edgeAttribute:
                        d = edgeAttribute['d']
                        if d == 'boolean':
                            value = value.lower() == 'true'
                    self.ndex_gsmall_searched.set_edge_attribute(id,name,value)

        edge_attributes_cx = None

    #TODO simplify this method
    def load_filtered_function_terms(self):
        '''

        :return:
        :rtype:
        '''
        if('functionTerms' in self.aspect_list):
            function_term_list = []
            self.metadata_dict['functionTerms'] = 0
            functionTerms_cx =  self.load_aspect('functionTerms')
            if(len(functionTerms_cx) > 0):
                for function_term in functionTerms_cx:
                    id = function_term.get('po')
                    if(self.searched_node_map.get(id) is not None):
                        function_term_list.append(function_term)

                self.ndex_gsmall_searched.create_from_aspects(function_term_list, 'functionTerms')

        functionTerms_cx = None

    #TODO simplify this method
    def load_filtered_citations(self):
        ''' Filter the citations, nodeCitations and edgeCitations
        Filter criteria depends on the nodeCitations and edgeCitations.  If a citation shows up in
        a valid search node (1-step, 2-step, etc...) then the corresponding citation is included.
        Likewise for edgeCitations

        :return: None
        :rtype: None
        '''
        if('nodeCitations' in self.aspect_list):
            self.metadata_dict['nodeCitations'] = 0
            nc_aspect =  self.load_aspect('nodeCitations')
            for nc in nc_aspect:
                found_nc = False
                for nc_po in nc.get('po'):
                    if(self.searched_node_map.get(nc_po) is not None):
                        found_nc = True
                        if(nc.get('citations') is not None):
                            #print str(nc_po)
                            for nc_citation in nc.get('citations'):
                                if(self.citation_map.get(nc_citation) is None):
                                    self.citation_map[nc_citation] = 0
                if(found_nc):
                    self.filtered_node_citation_list.append(nc)

            if(len(self.filtered_node_citation_list) > 0):
                self.ndex_gsmall_searched.create_from_aspects(self.filtered_node_citation_list, 'nodeCitations')

        if('edgeCitations' in self.aspect_list):
            self.metadata_dict['edgeCitations'] = 0
            ec_aspect =  self.load_aspect('edgeCitations')
            for ec in ec_aspect:
                found_ec = False
                for ec_po in ec.get('po'):
                    if(self.searched_edge_map.get(ec_po) is not None):
                        found_ec = True
                        if(ec.get('citations') is not None):
                            for ec_citation in ec.get('citations'):
                                if(self.citation_map.get(ec_citation) is None):
                                    self.citation_map[ec_citation] = 0
                if(found_ec):
                    self.filtered_edge_citation_list.append(ec)

            if(len(self.filtered_edge_citation_list) > 0):
                self.ndex_gsmall_searched.create_from_aspects(self.filtered_edge_citation_list, 'edgeCitations')

        if('citations' in self.aspect_list):
            self.metadata_dict['citations'] = 0
            c_aspect =  self.load_aspect('citations')
            for c in c_aspect:
                #print c['@id']
                if(self.citation_map.get(c['@id']) is not None):
                    #print '      ' + str(c['@id'])
                    self.filtered_citation_list.append(c)

            if(len(self.filtered_citation_list) > 0):
                self.ndex_gsmall_searched.create_from_aspects(self.filtered_citation_list, 'citations')

        nc_aspect = None
        ec_aspect = None
        c_aspect = None

    #TODO simplify this method
    def load_filtered_support(self):
        '''

        :return: None
        :rtype: None
        '''

        filtered_node_supports = []
        if('nodeSupports' in self.aspect_list):
            self.metadata_dict['nodeSupports'] = 0
            ns_aspect =  self.load_aspect('nodeSupports')
            for ns in ns_aspect:
                found_ns = False
                for ns_po in ns.get('po'):
                    if(self.searched_node_map.get(ns_po) is not None):
                        found_ns = True

                        # Add the citation to the map
                        for ns_supports in ns.get('supports'):
                            if(self.supports_map.get(ns_supports) is None):
                                self.supports_map[ns_supports] = 0

                if(found_ns):
                    filtered_node_supports.append(ns)

            if(len(filtered_node_supports) > 0):
                self.ndex_gsmall_searched.create_from_aspects(filtered_node_supports, 'nodeSupports')

        filtered_edge_supports = []
        if('edgeSupports' in self.aspect_list):
            self.metadata_dict['edgeSupports'] = 0
            es_aspect =  self.load_aspect('edgeSupports')
            for es in es_aspect:
                found_es = False
                for es_po in es.get('po'):
                    if(self.searched_node_map.get(es_po) is not None):
                        found_es = True

                        # Add the citation to the map
                        for es_supports in es.get('supports'):
                            if(self.supports_map.get(es_supports) is None):
                                self.supports_map[es_supports] = 0

                if(found_es):
                    filtered_edge_supports.append(es)

            if(len(filtered_edge_supports) > 0):
                self.ndex_gsmall_searched.create_from_aspects(filtered_edge_supports, 'edgeSupports')

        filtered_supports = []
        if('supports' in self.aspect_list):
            self.metadata_dict['supports'] = 0
            s_aspect =  self.load_aspect('supports')
            for s in s_aspect:
                if(self.supports_map.get(s['@id']) is not None):
                    filtered_supports.append(s)

                    if(self.citation_map.get(s['citation']) is None):
                        self.citation_map[s['citation']] = 0



    #=====================================
    # SEARCH NETWORK FOR n-STEP NEIGHBORS
    #=====================================
    '''returns the found nodes and their 1-step neighbors'''
    def search_full_attribute_network(self, search_terms, depth=1):
        search_terms_array = [self.get_node_id_by_value(sn) for sn in search_terms.split(',')]

        aspect_list = self.get_aspects()

        #==========================================
        # GET THE NODES in the n-step neighborhood
        #==========================================
        n = self.ndex_gsmall.nodes()
        for i in range(depth):
            subgraph_nodes = []
            for term_id in search_terms_array:
                if(term_id in n):
                    subgraph_nodes.append(term_id)
                    add_these_nodes = self.ndex_gsmall.neighbors(term_id)
                    for add_node in add_these_nodes:
                        if(add_node not in subgraph_nodes):
                            subgraph_nodes.append(add_node)

            search_terms_array = subgraph_nodes

        #filtered_edge_ids = self.get_filtered_edge_ids(subgraph_nodes)

        ndex_gsmall_sub = self.ndex_gsmall.subgraph_new(subgraph_nodes)

        sub_nodes = ndex_gsmall_sub.nodes()
        remove_these_nodes = []
        keep_these_nodes = []
        for full_node in self.ndex_gsmall.nodes():
            if(full_node not in sub_nodes):
                remove_these_nodes.append(full_node)
            else:
                keep_these_nodes.append(full_node)

        self.ndex_gsmall_searched = self.ndex_gsmall#.copy()

        self.ndex_gsmall_searched.remove_nodes_from(remove_these_nodes)

        print 'edges: ' + str(len(self.ndex_gsmall_searched.edges()))

        return self.ndex_gsmall_searched.to_cx()

    def get_filtered_edge_ids(self, n_id_list):
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
        if(len(self.nodes) > 0):
            if(self.nodes[0].get('n') is None):
                return value

        item = next((x for x in self.nodes if x.get('n') == value), None)
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



