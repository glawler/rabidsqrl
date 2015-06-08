import logging
import urllib.parse
from .stealth_engine import StealthEngine

log = logging.getLogger(__name__)

class AttackException(Exception):
    pass

class Attack(object):

    attack_name = None

    def __init__(self, config_entry):
        self.attack = None
        for k, v in config_entry.items():
            setattr(self, k, v)

        self._confirm_config()
        self._se = StealthEngine(config_entry)

    def _confirm_config(self):
        req = ['attribute', 'base_url']
        for r in req:
            if not getattr(self, r, False):
                raise AttackException('Missing configuration {} required for attack.'.format(r))

    def next_url(self):
        '''Yield the next URL statement in the attack. May block if stealth engine is enabled.'''
        for sql in self.next_sql():
            params = urllib.parse.urlencode({self.attribute: sql})
            url = '{}?{}'.format(self.base_url, params)
            yield url
            self._se.wait_interval();

    def handle_response(self, response, sql):
        '''Handle the response. Return non-zero to stop processing. If non-zero,
        you can specify an error string.'''
        log.debug('Ignoring response in Attack base class.')
        return 0, ''

    def __repr__(self):
        return '<Attack(name={})>'.format(self.attack)
