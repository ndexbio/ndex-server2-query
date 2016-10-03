__author__ = 'aarongary'
import unittest
import warnings
from bson.json_util import dumps
import json
import pymongo
import time
import os
from app.FileRepo import NDExFileRepository
from ndex.networkn import NdexGraph
from app import repo_directory
import pysolr
from app import solr_url

class ScratchTests(unittest.TestCase):

    def test_compare_cx_to_aspect_built(self):
        solr = pysolr.Solr(solr_url + '6503ea84-84f8-11e6-acec-06832d634f41/', timeout=10)
        results = solr.search('YGL122C,YGR218W')
        node_ids = [n['id'] for n in results.docs]
        print node_ids


        print '------------------------'
        print '- Compare CX to Aspect -'
        print '------------------------'
        test_data = [
            {'uuid': '6503ea84-84f8-11e6-acec-06832d634f41', 'search_string': 'YGL122C,YGR218W,YNL216W'}
        ]

        #=======================
        # Aspect built network
        #=======================
        start_time = time.time()
        for test_item in test_data:
            start_time = time.time()
            print '- Load file ' + test_item['uuid']
            ndexFileRepository = NDExFileRepository(test_item['uuid'])

            print '- Aspect built time: ' + str(time.time() - start_time)
            start_time = time.time()
            #print ' '
            #print ' '

            searched_cx = ndexFileRepository.search_network(test_item['search_string'], 3)
            searched_gsmall = NdexGraph(searched_cx)
            self.assertGreater(len(searched_gsmall.edges()), 0)

        print 'Search network: ' + str(time.time() - start_time)
        print ' '

        #======================================
        # CX built network
        #======================================
        start_time = time.time()
        for test_item in test_data:
            start_time = time.time()
            print '- Load file ' + test_item['uuid']
            ndexFileRepository = NDExFileRepository(test_item['uuid'], True)

            print '- CX built time ' + str(time.time() - start_time)
            start_time = time.time()
            #print ' '
            #print ' '

            searched_cx = ndexFileRepository.search_full_attribute_network(test_item['search_string'], 3)
            searched_gsmall = NdexGraph(searched_cx)
            self.assertGreater(len(searched_gsmall.edges()), 0)

        print 'Search network: ' + str(time.time() - start_time)


        #ndexFileRepository.get_aspects()
        #nodes = ndexFileRepository.load_aspect('nodes')
        #print ndexFileRepository.get_node_value_by_id(1)
        #print ndexFileRepository.get_nodes_and_edges().edges()

        print '------------------------'
        print '- END Compare          -'
        print '------------------------'
        print ' '
        print ' '

        #self.assertTrue(True)

    #==============================
    # TEST REPO
    #==============================
    def test_create_from_aspect(self):
        #===================================
        # LOAD NETWORK FROM ASPECTS
        #===================================
        #
        print '- loading full network'
        start_time = time.time()
        ndexFileRepository = NDExFileRepository('3c572160-75cc-11e6-ad66-06832d634f41')
        aspect_based_network = ndexFileRepository.get_ndex_gsmall()
        cx1 = aspect_based_network.to_cx()
        print str(start_time - time.time())

        edge_attributes1 = []
        node_attributes1 = []
        for cx_item in cx1:
            if('edgeAttributes' in cx_item):
                edge_attributes1.append(cx_item)

            if('nodeAttributes' in cx_item):
                node_attributes1.append(cx_item)

        print 'Aspect generated node count'
        print len(aspect_based_network.nodes())
        print len(edge_attributes1)
        print len(node_attributes1)

        #===================================
        # LOAD NETWORK FROM *.CX FILE
        #===================================
        ndexFileRepository2 = NDExFileRepository('3c572160-75cc-11e6-ad66-06832d634f41', True)
        cx_based_network = ndexFileRepository2.get_ndex_gsmall()
        cx2 = cx_based_network.to_cx()

        edge_attributes2 = []
        node_attributes2 = []
        for cx_item in cx2:
            if('edgeAttributes' in cx_item):
                edge_attributes2.append(cx_item)

            if('nodeAttributes' in cx_item):
                node_attributes2.append(cx_item)

        print 'CX generated node count'
        print len(cx_based_network.nodes())
        print len(edge_attributes2)
        print len(node_attributes2)
        print ' '
        print ' '

        self.assertEqual(len(cx_based_network.nodes()), len(aspect_based_network.nodes()))
        self.assertEqual(len(cx_based_network.edges()), len(aspect_based_network.edges()))
        #self.assertEqual(len(edge_attributes2), len(edge_attributes1))
        #self.assertEqual(len(node_attributes2), len(node_attributes1))

    def test_search_network(self):
        test_data = [
            {'uuid': '02bd6402-7174-11e6-9178-06832d634f41', 'search_string': 'HDAC2'},
            {'uuid': '3c572160-75cc-11e6-ad66-06832d634f41', 'search_string': 'PSG11,AGK'},
            {'uuid': '03cc14e8-7174-11e6-9178-06832d634f41', 'search_string': 'DPYSL3,DCN,NID2'},
            {'uuid': '03f6c8b3-76e2-11e6-ad66-06832d634f41', 'search_string': 'ART3,LONRF1,ATP8A2'}
        ]
        for test_item in test_data:
            start_time = time.time()
            print '- Load file ' + test_item['uuid']
            ndexFileRepository = NDExFileRepository(test_item['uuid'])

            print '- Search network ' + str(time.time() - start_time)
            print ' '
            print ' '

            searched_cx = ndexFileRepository.search_network(test_item['search_string'], 1)
            searched_gsmall = NdexGraph(searched_cx)
            self.assertGreater(len(searched_gsmall.edges()), 0)

        #ndexFileRepository.get_aspects()
        #nodes = ndexFileRepository.load_aspect('nodes')
        #print ndexFileRepository.get_node_value_by_id(1)
        #print ndexFileRepository.get_nodes_and_edges().edges()

        self.assertTrue(True)


