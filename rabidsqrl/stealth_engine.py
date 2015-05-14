import logging
import random   # for eval of interval
from time import sleep

log = logging.getLogger(__name__)

class StealthEngineException(Exception):
    pass

class StealthEngine(object):
    def __init__(self, config):
        # This is confusing, sorry. For each stealth config setting, we set an object attribute
        # the compiled code that is expressed in the config setting. For example if there is a 
        # "stealth_interval" defined in the config, there will be a self._interval_code that exists
        # in this object instance. That code can be eval'd to get a value.
        for conf, attr in [('stealth_interval', '_interval_code'), ('stealth_size', '_message_size_code')]:
            setattr(self, attr, None)
            if conf in config:
                c = config[conf]
                try:
                    setattr(self, attr, compile(c, '<string>', 'eval'))
                except Exception as e:
                    raise StealthEngineException('Error compiling expression "{}": {}'.format(c, e))

                log.debug('Set {} to {}'.format(conf, c))

    def wait_interval(self):
        if self._interval_code:
            try:
                interval = eval(self._interval_code)
            except Exception as e:
                raise StealthEngineException('Error evaluating interval expression: {}'.format(e))

            if interval > 0:
                log.debug('Sleeping for {} second(s).'.format(interval))
                sleep(interval)

    def has_message_size(self):
        return getattr(self, '_message_size_code', False)

    def message_size(self):
        if self._message_size_code:
            try:
                size = eval(self._message_size_code)
            except Exception as e:
                raise StealthEngineException('Error evaluating size expression: {}'.format(e))
        else:
            raise StealthEngineException('Called message_size() without setting a size function.')

        return int(size)
