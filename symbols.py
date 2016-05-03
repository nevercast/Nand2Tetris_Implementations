# coding=utf-8
""" Async symbol map with Futures for 1-pass assembling """

import asyncio

DEFAULTS = {
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
    'SCREEN': 16384,
    'KBD': 24576
}


def __sinit__():
    """ Static initializer """
    for n in range(0, 16):
        DEFAULTS['R{}'.format(n)] = n

__sinit__()


class SymbolMap(object):
    """ Symbol Map uses late resolution through async futures
        to give symbols when they are available. Allows
        use of coroutines/Tasks to parse ahead without having
        addresses for symbols.

        Enables single-pass assembling.
    """

    map = {}

    def __init__(self):
        """ Initializes defaults """
        for symbol, address in DEFAULTS.items():
            self.set(symbol, address)

    def set(self, symbol, address):
        """ Set a symbol value. Can only be done once.
            Will raise a Runtime Error if a symbol is set more than once.
        """
        future = self.get(symbol)
        if future.done():
            raise RuntimeError('Multiple assignments to Symbol {}. {} when already {}'.format(
                symbol,
                address,
                future.result()
            ))
        future.set_result(address)

    def get(self, symbol) -> asyncio.Future:
        """ Get's a future representing a symbol """
        if symbol not in self.map:
            return self.map.setdefault(symbol, asyncio.Future())
        return self.map[symbol]

