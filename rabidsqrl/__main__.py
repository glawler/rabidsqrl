import argparse
import logging
import json

from sys import stdout, stderr

from .argParseLog import addLoggingArgs, handleLoggingArgs
from .config import Config
from .attack import AttackException
from .attack_factory import AttackFactory

log = logging.getLogger(__name__)

if __name__ == '__main__':   # this should alwasy be the case, but what the hell.
    ap = argparse.ArgumentParser(prog='rabidsqrl', description='rabidsqlr - an SQL Injection tool')
    ap.add_argument('-c', '--config', help='Path to the configuration file.')
    ap.add_argument('-g', '--generate', action='store_true', help='Write a sample config file to stdout.')
    addLoggingArgs(ap)

    args = ap.parse_args()
    handleLoggingArgs(args)

    if args.generate:
        c = Config()
        Config.sample(stdout)
        exit(0)

    if not args.config:
        print('You need to specify a config file on the command line via the -c or --config arugment.', file=stderr)
        exit(1)

    log.debug('Reading configuration from {}.'.format(args.config))

    try:
        with open(args.config, 'r') as fd:
            conf = json.load(fd)
    except FileNotFoundError:
        print('Error opening config file {}. Unable to continue.'.format(args.config), file=stderr)
        exit(2)
    except ValueError as e:
        print('Error parsing config: {}'.format(e), file=stderr)
        exit(2)

    log.debug('conf: {}'.format(conf))

    # quick sanity check of config - all entries need a host and attack.
    if [entry for entry in conf if 'host' not in entry or 'attack' not in entry]:
        print('Missing "host" or "attack" in at least one config entry.')
        exit(3)

    for entry in conf:
        log.debug('Running attack against {}.'.format(entry['host']))
        try:
            AttackFactory(entry).doAttack()
        except AttackException as e:
            print('Error in attack: {}'.format(e), file=stderr)
            exit(4)

    exit(0)
