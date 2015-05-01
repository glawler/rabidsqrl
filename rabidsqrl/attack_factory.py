import logging
from .config import Config
from .sqlinjection import SQLInjection
from .stealth_engine import StealthEngine

log = logging.getLogger(__name__)

def AttackFactory(config):
    if 'attack' not in config:
        msg = 'Missing "attack" entry in config file.'
        raise AttackException(msg)

    se = StealthEngine()
    if 'stealth_interval' in config:
        se.interval = config['stealth_interval']

    if config['attack'] == SQLInjection.name:
        return SQLInjection(config, se)

    raise AttackException('Attack {} not supported.'.format(config['attack']))
