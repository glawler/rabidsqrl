import logging
import json

log = logging.getLogger(__name__)

class Config(object):
    def __init__(self):
        pass

    def sample(fd):
        c = [{
                'host': 'wpvuln', 
                'base_url': 'http://wpvuln',
                'attribute': 'thisisnotgood',
                'attack': 'sqlinjection',
                'stealth': '1',
             }
        ]
        log.debug('sample {}'.format(c))
        json.dump(c, fd, indent=4)
