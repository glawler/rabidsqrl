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
                'attribute': 'inline',
                'stealth_interval': 'random.normalvariate(5, 1.8)+3',
                'attack': 'sqlinjection',
                'statements': [
                    "create table inconspicuous (data text) --",
                    "insert into inconspicuous(data) values('hello')--",
                    "insert into inconspicuous(data) values('world')--"
                ]

             }
        ]
        log.debug('sample {}'.format(c))
        json.dump(c, fd, indent=4)
