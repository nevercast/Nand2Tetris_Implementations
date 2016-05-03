# coding=utf-8
""" Does the actual assembling """
import sys
import asyncio

import code
import parse
import symbols

CODE_BASE_ADDRESS = 0
variable_address = 16

RUNNING = True  # Only used for a Windows fix -.-" freaking windows man!


def variable_provider(symbol_map: symbols.SymbolMap, symbol):
    """ Variable address provider callback for variable allocation. """
    global variable_address
    symbol_map.set(symbol, variable_address)
    variable_address += 1


map = symbols.SymbolMap(variable_provider)


async def resolve_operation(pline: parse.ParserLine, code_address):
    """ Do the work that takes assembly input and generates the output """

    # Pre-Processing
    if pline.line_type == 'load_symbol':  # If a symbol is defined. Resolve it and yield if it's not ready yet.
        pline.constant = await map.get(pline.symbol)
        pline.line_type = 'load_constant'

    # Assembling
    if pline.line_type == 'load_constant':
        return code.emit_a(pline.constant)
    elif pline.line_type == 'compute':
        return code.emit_c(pline.computation, pline.destination, pline.jump_condition)
    elif pline.line_type == 'label':
        # Set the label to our current address
        # This will trigger any parallel tasks waiting for this symbol in a map.get()
        map.set(pline.symbol, code_address)

@asyncio.coroutine
def assemble(filename):
    # Create a parser
    parser = parse.Parser(filename)
    address = CODE_BASE_ADDRESS  # Every operation is a single int. Makes addresses lovely
    tasks = []  # Running tasks
    for parser_line in parser.parse():  # Queue parallel processing of all the lines
        tasks.append(asyncio.ensure_future(resolve_operation(parser_line, address)))
        if parser_line.line_type != 'label':    # Slight trample on separation of concerns
            address += 1                        # But it does save a lot of work undoing what I've done.

    # In a chain (in order), emit the completed tasks.
    # If lines 1, 2 and 4 are parsed. The first two will be emitted
    # Once line 3 is completed, 3 and 4 will be emitted. etc.
    for task in tasks:
        result = yield from task
        if result is not None:
            print(result)

# Python has a documented bug with Windows Keyboard Interrupts.
# This prevents interrupts being ignored (allows Ctrl+C to work)
async def _windows_kb_interrupt_fix():
    while RUNNING:
        await asyncio.sleep(1)

try:
    if len(sys.argv) < 2:
        raise RuntimeError('No target file provided')
    read_file = sys.argv[1]
    loop = asyncio.get_event_loop()
    kb_task = asyncio.ensure_future(_windows_kb_interrupt_fix())
    loop.run_until_complete(assemble(read_file))
    # We've finished. So close the keyboard task
    RUNNING = False
    loop.run_until_complete(kb_task)
except KeyboardInterrupt:
    pass
except Exception as e:
    print('Failed to assemble target')
    print('Syntax: python assembler.py input.asm')
    print('Output will be input.jack')
    print('Error:')
    print(e)

