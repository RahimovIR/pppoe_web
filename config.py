import logging
import os
import sys

import web

env = os.environ.get("WEB_ENV", "development")
print "Environment: %s" % env

logging.basicConfig(filename='logs/%s.log' % env, level=logging.DEBUG)
logger = logging.getLogger('webpy-skeleton')

# Default settings. Override below
web.config.debug = True
cache = False

