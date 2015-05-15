import argparse
import logging
import yaml

from sys import stdout, stderr

from .argParseLog import addLoggingArgs, handleLoggingArgs
from .attack import AttackException
from .attack_factory import AttackFactory
from .connection_engine import ConnectionEngine

log = logging.getLogger(__name__)

if __name__ == '__main__':   # this should alwasy be the case, but what the hell.
    ap = argparse.ArgumentParser(prog='rabidsqrl', description='rabidsqlr - an SQL Injection tool')
    ap.add_argument('-c', '--config', help='Path to the configuration file.')
    ap.add_argument('-r', '--results', action='store_true', help='Show results of attack on stdout.')
    addLoggingArgs(ap)

    args = ap.parse_args()
    handleLoggingArgs(args)

    if not args.config:
        print('You need to specify a config file on the command line via the -c or --config arugment.', file=stderr)
        exit(1)

    log.debug('Reading configuration from {}.'.format(args.config))

    try:
        with open(args.config, 'r') as fd:
            conf = yaml.load(fd)
    except FileNotFoundError:
        print('Error opening config file {}. Unable to continue.'.format(args.config), file=stderr)
        exit(2)
    except ValueError as e:
        print('Error parsing config: {}'.format(e), file=stderr)
        exit(3)

    log.debug('conf: {}'.format(conf))

    # quick sanity check of config - all entries need a host and attack.
    if [entry for entry in conf if 'attack' not in entry]:
        print('Missing "attack" in at least one config entry.')
        exit(4)

    attacks = []
    for entry in conf:
        try:
            attacks.append(AttackFactory(entry))
        except AttackException as e:
            print('Error in attack: {}'.format(e), file=stderr)
            exit(5)

    ce = ConnectionEngine(attacks, show_results=args.results)
    exit(ce.do_attacks())
