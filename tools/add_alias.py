#!/usr/bin/env python2
"""
Add alias to ledger
"""
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, SUPPRESS
import logging
import sys

from ledger import Ledger


def parse_arguments():
    parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('-l', '--logging', help='logging.level', default='WARNING')
    parser.add_argument('-f', '--file', help='file with JSON ledger to load (or stdin)', default=SUPPRESS)
    parser.add_argument('-o', '--output', help='file where to write JSON ledger (or stdout)', default=SUPPRESS)

    parser.add_argument('-a', '--alias', help='alias to add (repeatable)', metavar=('ALIAS', 'FULLNAME'),
                        action='append', nargs=2, default=SUPPRESS)

    return vars(parser.parse_args())


if __name__ == '__main__':
    config = parse_arguments()

    input_file = config.pop('file', '')
    output = config.pop('output', '')
    logging_level = config.pop('logging')
    aliases = config.pop('alias', [])

    logging.basicConfig(
        format='%(levelname)s:%(asctime)s:%(message)s', stream=sys.stdout,
        level=getattr(logging, logging_level.upper()))

    logging.info('Loading JSON ledger from {}'.format(input_file or 'standard input'))
    ledger = Ledger.from_json_file(input_file) if input_file else Ledger.from_json_string(sys.stdin.read())
    for a in aliases:
        ledger.add_alias(a[0], a[1])

    logging.info('Writing JSON ledger to {}'.format(output or 'standard output'))
    if output:
        with open(output, 'w') as f:
            f.write(str(ledger))
    else:
        print ledger
