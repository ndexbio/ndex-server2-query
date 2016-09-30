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

        self.assertTrue(True)
