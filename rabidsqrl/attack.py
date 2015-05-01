import logging

log = logging.getLogger(__name__)

class AttackException(Exception):
    pass

class Attack(object):

    name = None

    def __init__(self):
        pass

    def doAttack(self):
        raise AttackException('doAttack() called on base Attack class. Should not happen.')
        pass
