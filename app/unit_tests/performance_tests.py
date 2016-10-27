__author__ = 'aarongary'

import unittest
import requests
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
from pysolr import SolrError
from ndex import client as nc
from ndex.networkn import NdexGraph
import numpy as np

class PerformanceTests(unittest.TestCase):
    #==============================
    # TEST LARGE NETWORK
    #==============================
    def test_large_dev_vs_dev2(self):
        root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        test_doc_path = os.path.join(root, 'test_docs')
        result_times = {'d_1':[],'d_2':[],'d_3':[],'d2_1':[],'d2_2':[],'d2_3':[]}
        print root
        print test_doc_path

        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'Cache-Control': 'no-cache',
                   }

        self.s = requests.session()
        self.s.auth = ("aarongary", "ccbbucsd")

        #=======================================
        # DEV
        #=======================================
        url = "http://dev.ndexbio.org/v2/search/network/018e3dc5-94b1-11e6-abed-06832d634f41/query?size=500"
        post_json = {
            "searchString":  "TP53,CDK4,AKT1",
            "searchDepth": 1,
            "edgeLimit":  58000
        }

        for i in range(1):
            print '--------DEV----------------'
            start_time = time.time()
            post_json["searchDepth"] = 1
            self.run_pack(url, post_json, headers, test_doc_path + '/dev_depth1.cx')
            result_times['d_1'].append(time.time() - start_time)
            print 'Response time (Large - Depth 1): ' + str(time.time() - start_time)

            start_time = time.time()
            post_json["searchDepth"] = 2
            self.run_pack(url, post_json, headers, test_doc_path + '/dev_depth2.cx')
            result_times['d_2'].append(time.time() - start_time)
            print 'Response time (Large - Depth 2): ' + str(time.time() - start_time)

            start_time = time.time()
            post_json["searchDepth"] = 3
            self.run_pack(url, post_json, headers, test_doc_path + '/dev_depth3.cx')
            result_times['d_3'].append(time.time() - start_time)
            print 'Response time (Large - Depth 3): ' + str(time.time() - start_time)

        print 'd_1 average: ' + str(np.array(result_times['d_1']).mean())
        print 'd_2 average: ' + str(np.array(result_times['d_2']).mean())
        print 'd_3 average: ' + str(np.array(result_times['d_3']).mean())

        #=======================================
        # DEV2
        #=======================================
        self.s.close()

        self.s = requests.session()
        self.s.auth = ("aarongary1", "ccbbucsd")

        url2 = "http://dev2.ndexbio.org/rest/network/2ddcb5a9-94b1-11e6-93d8-0660b7976219/asNetwork/query"

        print '--------DEV2---------------'
        for i in range(0):
            start_time = time.time()
            post_json["searchDepth"] = 1
            self.run_pack(url2, post_json, headers, None) # test_doc_path + '/dev2_depth1.cx')
            result_times['d2_1'].append(time.time() - start_time)
            print 'Response time (Large - Depth 1): ' + str(time.time() - start_time)

            start_time = time.time()
            post_json["searchDepth"] = 2
            self.run_pack(url2, post_json, headers, None)#test_doc_path + '/dev2_depth2.cx')
            result_times['d2_2'].append(time.time() - start_time)
            print 'Response time (Large - Depth 2): ' + str(time.time() - start_time)

            start_time = time.time()
            post_json["searchDepth"] = 3
            self.run_pack(url2, post_json, headers, test_doc_path + '/dev2_depth3.cx')
            result_times['d2_3'].append(time.time() - start_time)
            print 'Response time (Large - Depth 3): ' + str(time.time() - start_time)

        print 'd2_1 average: ' + str(np.array(result_times['d2_1']).mean())
        print 'd2_2 average: ' + str(np.array(result_times['d2_2']).mean())
        print 'd2_3 average: ' + str(np.array(result_times['d2_3']).mean())

        print dumps(result_times)

    def run_pack(self, url, post_json, headers, test_doc_path):

        response = self.s.post(url,json=post_json, headers=headers)

        if(test_doc_path is not None):
            dev_depth = response.json()

            downloadsTxt = open(test_doc_path, 'w')
            downloadsTxt.write(dumps(dev_depth))
            downloadsTxt.close()

    def test_metrics(self):
        root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        test_doc_path = os.path.join(root, 'test_docs')
        self.get_network_metadata('dev_depth2.cx', test_doc_path, '2.0')

    def get_network_metadata(self, cx_file_name, test_doc_path, version):
        print cx_file_name

        read_this_aspect = os.path.join(test_doc_path, cx_file_name)
        d = None
        with open(read_this_aspect, 'rt') as fid:
            d = json.load(fid)
            if(version == '1.3'):
                edges = d.get('edgeCount')
                nodes = d.get('nodeCount')
                print 'There are ' + str(nodes) + ' Nodes and ' + str(edges) + ' Edges'
            else:
                ndex_gsmall = NdexGraph(d.get('data'))

                print 'There are ' + str(len(ndex_gsmall.nodes())) + ' Nodes and ' + str(len(ndex_gsmall.edges())) + ' Edges'

            fid.close()

    def test_dev_vs_dev2(self):
        #ndex = nc.Ndex("http://dev.ndexbio.org","aarongary", "ccbbucsd")

        #ndex.post("/v2/search/network/9ae4fea6-8cb0-11e6-a9fe-06832d634f41/query?size=500", )
        print '--------DEV----------------'
        start_time = time.time()

        headers = {'Content-Type': 'application/json',
                   'Accept': 'application/json',
                   'Cache-Control': 'no-cache',
                   }

        self.s = requests.session()
        self.s.auth = ("aarongary", "ccbbucsd")

        url = "http://dev.ndexbio.org/v2/search/network/9ae4fea6-8cb0-11e6-a9fe-06832d634f41/query?size=500"
        post_json = {
            "searchString":  "TP53,CDK4,AKT1",
            "searchDepth": 3,
            "edgeLimit":  500
        }

        response = self.s.post(url,json=post_json, headers=headers)

        print 'Response time: ' + str(time.time() - start_time)
        start_time = time.time()

        post_json = {
            "searchString":  "TP53,CDK4,AKT1",
            "searchDepth": 2,
            "edgeLimit":  500
        }

        response = self.s.post(url,json=post_json, headers=headers)

        print 'Response time: ' + str(time.time() - start_time)
        start_time = time.time()

        post_json = {
            "searchString":  "TP53,CDK4,AKT1",
            "searchDepth": 1,
            "edgeLimit":  500
        }

        response = self.s.post(url,json=post_json, headers=headers)

        print 'Response time: ' + str(time.time() - start_time)
        print '--------DEV2---------------'
        start_time = time.time()

        #print dumps(response.json())


        #=======================================
        # DEV2
        #=======================================

        start_time = time.time()

        self.s2 = requests.session()
        self.s2.auth = ("aarongary", "ccbbucsd")

        url2 = "http://dev2.ndexbio.org/network/10180a3b-8fcc-11e6-93d8-0660b7976219/asNetwork/query"
        post_json2 = {
            "searchString":  "TP53,CDK4,AKT1",
            "searchDepth": 3,
            "edgeLimit":  500
        }

        response = self.s2.post(url,json=post_json2, headers=headers)

        print 'Response time: ' + str(time.time() - start_time)

        start_time = time.time()

        post_json2 = {
            "searchString":  "TP53,CDK4,AKT1",
            "searchDepth": 2,
            "edgeLimit":  500
        }

        response = self.s2.post(url,json=post_json2, headers=headers)
        print 'Response time: ' + str(time.time() - start_time)

        start_time = time.time()

        post_json2 = {
            "searchString":  "TP53,CDK4,AKT1",
            "searchDepth": 1,
            "edgeLimit":  500
        }

        response = self.s2.post(url,json=post_json2, headers=headers)
        print 'Response time: ' + str(time.time() - start_time)

        self.assertTrue(True)
