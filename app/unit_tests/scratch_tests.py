__author__ = 'aarongary'
import unittest
import warnings
from bson.json_util import dumps
import json
import pymongo
from app.FileRepo import NDExFileRepository

class ScratchTests(unittest.TestCase):
    #==============================
    # TEST REPO
    #==============================
    def test_repo_scratch(self):
        ndexFileRepository = NDExFileRepository('02bd6402-7174-11e6-9178-06832d634f41')

        ndexFileRepository.get_aspects()
        nodes = ndexFileRepository.load_aspect('nodes')

        print ndexFileRepository.get_node_value_by_id(1)

        print ndexFileRepository.get_nodes_and_edges().edges()

        ndexFileRepository.search_network('HDAC2')

        self.assertTrue(True)

