from .attack import AttackException
from .sqlinline_attack import SQLInlineAttack
from .filewrite_attack import FileWriteAttack

def AttackFactory(config):
    if 'attack' not in config:
        raise AttackException('Missing "attack" entry in config file.')

    attack = config['attack']

    attack_map = {
        SQLInlineAttack.attack_name: SQLInlineAttack,
        FileWriteAttack.attack_name: FileWriteAttack
    }

    if attack not in attack_map.keys():
        raise AttackException('Attack {} not supported.'.format(attack))

    return attack_map[attack](config)    # return an instance of the class.
