#!/usr/bin/env python2
"""
Create a JSON ledger
"""
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, SUPPRESS
import logging
import sys

from ledger import Ledger


def parse_arguments():
    parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('-l', '--logging', help='logging.level', default='WARNING')
    parser.add_argument('-o', '--output', help='file where to write JSON ledger (or stdout)', default=SUPPRESS)

    parser.add_argument('-a', '--author', help='Add author (repeatable)', metavar=('AUTHOR'), dest='authors', action='append', default=SUPPRESS)
    parser.add_argument('-i', '--id', help='Ledger id (if creating)', default=SUPPRESS)
    parser.add_argument('-D', '--date', help='Creation date', default=SUPPRESS)
    parser.add_argument('-d', '--description', help='Free-form description', default=SUPPRESS)
    parser.add_argument('-c', '--comment', help='Any comment here', default=SUPPRESS)

    return vars(parser.parse_args())


if __name__ == '__main__':
    config = parse_arguments()

    output = config.pop('output', None)
    logging_level = config.pop('logging')

    logging.basicConfig(
        format='%(levelname)s:%(asctime)s:%(message)s', stream=sys.stdout,
        level=getattr(logging, logging_level.upper()))

    ledger = Ledger(**config)

    logging.info('Writing JSON ledger to {}'.format(output or 'standard output'))
    if output:
        with open(output, 'w') as f:
            f.write(str(ledger))
    else:
        print ledger
