import logging
import urllib.request
import urllib.parse

log = logging.getLogger(__name__)

class ConnectionEngineException(Exception):
    pass

class ConnectionEngine(object):
    def __init__(self, attacks, show_results):
        self.attacks = attacks
        self.show_results = show_results

    def do_attacks(self):
        for attack in self.attacks:
            for url in attack.next_url():
                log.info('Sending request: {}'.format(url))
                with urllib.request.urlopen(url) as fd:
                    resp = fd.read()
                    log.info('Read {} bytes in response.'.format(len(resp)))

                    if self.show_results:
                        self._show_results(resp)

        return 0

    def _show_results(self, resp):
        print(resp)
