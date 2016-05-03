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
    variable_callback = None
    pending_symbols = set()

    def __init__(self, variable_provider = None):
        """ Initializes defaults """
        async def setup():
            for symbol, address in DEFAULTS.items():
                await self.set(symbol, address)
        asyncio.get_event_loop().run_until_complete(setup())
        self.variable_callback = variable_provider

    async def set(self, symbol, address, no_check=False):
        """ Set a symbol value. Can only be done once.
            Will raise a Runtime Error if a symbol is set more than once.
        """
        future = self.map[symbol] if no_check else await self.get(symbol)
        if future.done():
            raise RuntimeError('Multiple assignments to Symbol {}. {} when already {}'.format(
                symbol,
                address,
                future.result()
            ))
        self.pending_symbols.discard(symbol)
        future.set_result(address)

    async def get(self, symbol):
        """ Get's a future representing a symbol """
        if symbol in self.map:
            return self.map[symbol]
        self.pending_symbols.add(symbol)
        future = self.map.setdefault(symbol, asyncio.Future())
        # if self.variable_callback and symbol.islower():
        #    await self.variable_callback(self, symbol)
        return future

