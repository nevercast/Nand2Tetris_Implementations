# coding=utf-8
""" Converts mnemonics for dest, comp and jump in to binary """

C_COMMAND_PREFIX = '111'

COMP_MAP = {
    # a=0
    '0': '0101010',
    '1': '0111111',
    '-1': '0111010',
    'D': '0001100',
    'A': '0110000',
    '!D': '0001101',
    '!A': '0110001',
    '-D': '0001111',
    '-A': '0110011',
    'D+1': '0011111',
    'A+1': '0110111',
    'D-1': '0001110',
    'A-1': '0110010',
    'D+A': '0000010',
    'D-A': '0010011',
    'A-D': '0000111',
    'D&A': '0000000',
    'D|A': '0010101',
    # a=1
    'M': '1110000',
    '!M': '1110001',
    '-M': '1110011',
    'M+1': '1110111',
    'M-1': '1110010',
    'D+M': '1000010',
    'D-M': '1010011',
    'M-D': '1000111',
    'D&M': '1000000',
    'D|M': '1010101'
}

DEST_MAP = {
    None: '000',
    'M': '001',
    'D': '010',
    'MD': '011',
    'A': '100',
    'AM': '101',
    'AD': '110',
    'AMD': '111'
}

JUMP_MAP = {
    None: '000',
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'
}


def emit_c(_comp:str, _dest:str, _jump:str):
    """ Returns a binary representation of a C_COMMAND type"""
    try:
        return C_COMMAND_PREFIX + comp(_comp) + dest(_dest) + jump(_jump)
    except IndexError:
        raise RuntimeError('Failed to emit C({}={};{})'.format(_dest, _comp, _jump))

def emit_a(address:int):
    """ Emit an A command"""
    if address > 0x7FFF or address < 0:
        raise RuntimeError('Failed to emit A({}). Out of bounds.'.format(address))
    return '1{:015b}'.format(address)

# Implemented only because the PDF said I should.


def comp(_comp:str):
    """ Returns binary for comp command """
    return COMP_MAP[_comp]


def dest(_dest:str):
    """ Returns binary for dest command """
    return DEST_MAP[_dest]


def jump(_jump:str):
    """ Returns binary for jump command """
    return JUMP_MAP[_jump]