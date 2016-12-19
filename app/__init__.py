import os
import logging
import logging.handlers

root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
log_path = os.path.join(root, 'logs')
mongodb_uri = 'mongodb://localhost'
solr_url = 'http://preview.ndexbio.org:8983/solr/'
#solr_url = 'http://dev.ndexbio.org:8983/solr/'

#repo_directory = '/Users/aarongary/Development/DataSets/NDEx/server2/data/'
repo_directory = '/opt/ndex/data/'

#temp_append_path = '/Users/aarongary/Development/Projects/ndex-python/ndex'
temp_append_path = '/opt/ndex/query_engine/ndex-python/ndex'


def get_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    logger.handlers = []

    formatter = logging.Formatter('%(asctime)s.%(msecs)d ' + name + ' %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')

    handler = logging.handlers.TimedRotatingFileHandler(os.path.join(log_path, 'app.log'), when='midnight', backupCount=28)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
