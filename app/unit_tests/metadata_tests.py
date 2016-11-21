__author__ = 'aarongary'

import unittest
import requests
import warnings
import json
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

class MetadataTests(unittest.TestCase):
    #==============================
    # TEST LARGE NETWORK
    #==============================
    def test_large_dev_vs_dev2(self):
        ndexFileRepository = NDExFileRepository("317332f7-ade8-11e6-913c-06832d634f41", load_from_cx=True)

        #======================
        # NODE ATTRIBUTES
        #======================
        #ndexFileRepository.load_node_attributes()

        #======================
        # EDGE ATTRIBUTES
        #======================
        #ndexFileRepository.load_edge_attributes()

        aspect_based_network = ndexFileRepository.get_ndex_gsmall()
        cx1 = aspect_based_network.to_cx()

        self.assertTrue(True)
