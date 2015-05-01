import logging
import random   # for eval of interval
from time import sleep

log = logging.getLogger(__name__)

class StealthEngineException(Exception):
    pass

class StealthEngine(object):
    def __init__(self):
        self._interval_code = None
        self._interval = None

    @property
    def interval(self):         # probably don't need a getter for this.
        return self._interval

    @interval.setter
    def interval(self, i):
        log.debug('Setting stealth interval to {}'.format(i))
        try:
            self._interval_code = compile(i, '<string>', 'eval')
            self._interval = i
        except Exception as e:
            raise StealthEngineException('Error compiling interval expression "{}": {}'.format(i, e))

    def execute_sequence(self, func, statements):
        for i, s in enumerate(statements):
            func(s)

            if self._interval_code and i < len(statements)-1:
                try:
                    interval = eval(self._interval_code)
                except Exception as e:
                    raise StealthEngineException('Error evaluating interval expression: {}'.format(e))

                if interval > 0:
                    log.debug('Sleeping for {} second(s).'.format(interval))
                    sleep(interval)
