# coding=utf-8
""" Does the actual assembling """
import sys
from parse import Parser
import code

symbol_map = {
    'SP': 0,
    'LCL': 1,
    'ARG': 2,
    'THIS': 3,
    'THAT': 4,
    'SCREEN': 16384,
    'KBD': 24576
}

for n in range(0, 16):
    symbol_map['R{}'.format(n)] = n

def emit(binary:str):
    print('emit:', binary)

try:
    if len(sys.argv) < 2:
        raise RuntimeError('No target file provided')
    read_file = sys.argv[1]
    parzer = Parser(read_file)
    while parzer.hasMoreCommands():
        print('Assembling {}({})'.format(parzer.line, parzer.commandType))
        if parzer.commandType == 'A_COMMAND':
            if parzer.symbol:
                raise NotImplementedError('Symbols')
            else:
                emit(code.emit_a(parzer.constant))
        elif parzer.commandType == 'C_COMMAND':
            emit(code.emit_c(parzer.comp, parzer.dest, parzer.jump))
        elif parzer.commandType != 'NOOP':
            raise NotImplementedError(parzer.line)
        parzer.advance()
except Exception as e:
    print('Failed to assemble target')
    print('Syntax: python assembler.py input.asm')
    print('Output will be input.jack')
    print('Error:')
    print(e)

