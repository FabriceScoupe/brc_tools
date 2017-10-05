"""
Ledger module.
"""
from collections import OrderedDict
from datetime import datetime
import json
import logging
import uuid

VERSION = "1.0.0"


class Reference(OrderedDict):
    """
    A reference may be added to a transaction or the ledger.
    For instance, for a transaction, a reference could point to an invoice.
    For the overall ledger, a reference could point to a policy document.
    """
    def __init__(self, name, uri):
        super(Reference, self).__init__()
        self['name'] = name
        self['uri'] = uri
        logging.debug('Reference created: "name": {name}, "uri": {uri}'.format(**self))


class Detail(OrderedDict):
    """
    Can optionally added to a transaction, to break it down into items.
    For example, a cheque of 100 pounds to a sport retailer could be
    broken down into Detail("high-viz vest", 10.0, 5.0) and
    Detail("whistle", 5.0, 5.0) for instance.
    """
    def __init__(self, item, unit_price, quantity=1, unit=None):
        super(Detail, self).__init__()

        self['item'] = item
        self['unit-price'] = float(unit_price)
        self['quantity'] = float(quantity)
        if unit:
            self['unit'] = unit

        logging.debug('Detail created:\n{}'.format(self))

    def __str__(self):
        return json.dumps(self, indent=4, separators=(', ', ': '))


class Transaction(OrderedDict):
    """
    A debit or credit transaction, that may be added to the ledger.
    """
    def __init__(self, date, amount, **params):
        super(Transaction, self).__init__()
        self['amount'] = float(amount)
        self['date'] = date
        self['type'] = params.get('type', 'cheque')
        if 'id' in params:
            self['id'] = params.get('id')
        self['status'] = params.get('status', 'pending')

        for key in ['payee', 'payer', 'category', 'description', 'comments']:
            if key in params:
                self[key] = params[key]

        for key in ['labels', 'signed-by', 'references', 'details']:
            if key in params:
                self[key] = list(params[key])

        logging.debug('Transaction created:\n{}'.format(self))

    def __str__(self):
        return json.dumps(self, indent=4,  separators=(', ', ': '))

    @classmethod
    def from_object(cls, t):
        logging.debug('Transaction from {}'.format(t))
        date = t.pop('date')
        amount = t.pop('amount')
        return Transaction(date, amount, **t)

    def add_label(self, label):
        if "labels" in self:
            self["labels"].append(label)
        else:
            self["labels"] = [label]
        logging.debug('label [{}] added to Transaction:\n{}'.format(label, self))
        return self

    def add_reference(self, reference):
        if "references" in self:
            self["references"].append(reference)
        else:
            self["references"] = [reference]
        logging.debug('reference {} added to Transaction:\n{}'.format(reference['name'], self))
        return self

    def add_detail(self, detail):
        if "details" in self:
            self["details"].append(detail)
        else:
            self["details"] = [detail]
        logging.debug('detail {}: {} x {} added to Transaction:\n{}'.format(
            detail['item'], detail['unit-price'], detail['quantity'], self))
        return self

    def add_signee(self, signee):
        if "signed-by" in self:
            self["signed-by"].append(signee)
        else:
            self["signed-by"] = [signee]
        logging.debug('signee {} added to Transaction:\n{}'.format(signee, self))
        return self

    def set_status(self, new_status):
        self["status"] = new_status
        logging.debug('Transaction set to new status:\n{}'.format(self))
        return self


class Ledger(OrderedDict):
    """
    The overall account ledger.
    """
    def __init__(self, **params):
        super(Ledger, self).__init__()

        self["type"] = "ledger"
        self["id"] = params.get('id', 'ledger--' + str(uuid.uuid4()))
        self["date"] = params.get('date', datetime.utcnow().isoformat())
        self["version"] = params.get('version', VERSION)

        for key in ['description', 'comments']:
            if key in params:
                self[key] = params[key]

        for key in ['authors', 'transactions', 'aliases', 'references']:
            if key in params:
                self[key] = list(params[key])

    def __str__(self):
        return json.dumps(self, indent=4,  separators=(', ', ': '))

    @classmethod
    def from_object(cls, l):
        logging.debug('Ledger.from_object:\n{}'.format(json.dumps(l, indent=4, separators=(', ', ': '))))

        transactions = l.pop('transactions', [])
        references = l.pop('references', [])
        aliases = l.pop('aliases', [])

        ledger = Ledger(**l)

        for t in transactions:
            ledger.add_transaction(Transaction.from_object(t))

        for r in references:
            ledger.add_reference(Reference(r["name"], r["uri"]))

        if aliases:
            ledger["aliases"] = aliases

        return ledger

    @classmethod
    def from_json_string(cls, json_string):
        return Ledger.from_object(json.loads(json_string))

    @classmethod
    def from_json_file(cls, json_file):
        with open(json_file) as f:
            return Ledger.from_object(json.load(f))

    def add_transaction(self, transaction):
        if "transactions" in self:
            self["transactions"].append(transaction)
        else:
            self["transactions"] = [transaction]
        self["transactions"].sort(key=lambda t: t['date'])
        return self

    def add_reference(self, reference):
        if "references" in self:
            self["references"].append(reference)
        else:
            self["references"] = [reference]
        return self

    def add_alias(self, alias, full_name):
        if "aliases" in self:
            self["aliases"][alias] = full_name
        else:
            self["aliases"] = {alias: full_name}
        return self

