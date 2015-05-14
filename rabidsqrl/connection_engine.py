import logging
import urllib.request
import urllib.parse

log = logging.getLogger(__name__)

class ConnectionEngineException(Exception):
    pass

class ConnectionEngine(object):
    def __init__(self, attacks):
        self.attacks = attacks

    def do_attacks(self):
        for attack in self.attacks:
            for url in attack.next_url():
                log.info('Sending request: {}'.format(url))
                with urllib.request.urlopen(url) as fd:
                    resp = fd.read()
                    log.info('Read {} bytes in response.'.format(len(resp)))

        return 0
