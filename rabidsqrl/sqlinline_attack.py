import logging

from .attack import Attack, AttackException

log = logging.getLogger(__name__)

class SQLInlineAttackException(AttackException):
    pass

class SQLInlineAttack(Attack):

    attack_name = 'sql_inline'

    def __init__(self, config):
        super(SQLInlineAttack, self).__init__(config)

    def _confirm_config(self):
        super(SQLInlineAttack, self)._confirm_config()
        if not getattr(self, 'statements', False):
            raise SQLInlineAttack('Missing required "statements" in configuration for {} attack.'.format(
                SQLInlineAttack.attack_name))

    def next_sql(self):
        for s in self.statements:
            yield s
