#!/usr/bin/env python2
"""
Add transaction to ledger
"""
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, SUPPRESS
import logging
import sys

from ledger import Ledger, Transaction, Reference, Detail


def parse_arguments():
    parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument('date', help='date of transaction')
    parser.add_argument('amount', help='amount in GBP, negative for debit', type=float)

    parser.add_argument('-l', '--logging', help='logging.level', default='WARNING')
    parser.add_argument('-f', '--file', help='file with JSON ledger to load (or stdin)', default=SUPPRESS)
    parser.add_argument('-o', '--output', help='file where to write JSON ledger (or stdout)', default=SUPPRESS)

    parser.add_argument('-t', '--type', help='type, eg cheque, cash, direct-debit...', default='cheque')
    parser.add_argument('-i', '--id', help='transaction unique id for type, eg cheque no.', default=SUPPRESS)
    parser.add_argument('-s', '--status', help='status, eg pending, cancelled, settled', default='pending')
    parser.add_argument('-p', '--paye', help='payer(credit) or payee(debit)', default=SUPPRESS)

    parser.add_argument('-c', '--comments', help='Any comment here', default=SUPPRESS)
    parser.add_argument('-C', '--category', help='Category, eg fees, equipment, transport, premises', default=SUPPRESS)
    parser.add_argument('-d', '--description', help='Free-form description', default=SUPPRESS)

    parser.add_argument('-L', '--label', help='label (repeatable)', metavar=('LABEL',),
                        action='append', dest='labels', default=SUPPRESS)
    parser.add_argument('-S', '--signee', help='signee (repeatable)', metavar=('SIGNEE',),
                        action='append', dest='signed-by', default=SUPPRESS)
    parser.add_argument('-D', '--detail', help='detail (repeatable)', metavar=('ITEM', 'UNIT-PRICE', 'QUANTITY'),
                        action='append', dest='details', nargs=3, default=SUPPRESS)
    parser.add_argument('-r', '--reference', help='reference (repeatable)', metavar=('NAME', 'URI'),
                        action='append', dest='references', nargs=2, default=SUPPRESS)

    return vars(parser.parse_args())


if __name__ == '__main__':
    config = parse_arguments()

    input_file = config.pop('file', '')
    output = config.pop('output', '')
    logging_level = config.pop('logging')

    paye = config.pop('paye', None)
    if paye:
        if config['amount'] > 0.0:
            config['payer'] = paye
        else:
            config['payee'] = paye

    if 'details' in config:
        config['details'] = [Detail(*d) for d in config['details']]

    if 'references' in config:
        config['references'] = [Reference(*r) for r in config['references']]
        
    logging.basicConfig(
        format='%(levelname)s:%(asctime)s:%(message)s', stream=sys.stdout,
        level=getattr(logging, logging_level.upper()))

    logging.info('Loading JSON ledger from {}'.format(input_file or 'standard input'))
    ledger = Ledger.from_json_file(input_file) if input_file else Ledger.from_json_string(sys.stdin.read())

    ledger.add_transaction(Transaction.from_object(config))

    logging.info('Writing JSON ledger to {}'.format(output or 'standard output'))
    if output:
        with open(output, 'w') as f:
            f.write(str(ledger))
    else:
        print ledger
