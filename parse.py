# coding=utf-8
""" Parses Assembly lines and provides information about them """
import re


# Matches Alpha-Numeric, $, . and :
# The first letter cannot be decimal.
RGX_SYMBOL = r'[a-zA-Z$.:][\w$.:]+'

# @SYMBOL
RGX_COMMAND_A_SYMB = r'@(' + RGX_SYMBOL + ')'

# @CONSTANT
RGX_COMMAND_A_CONST = r'@(\d+)'

# (SYMBOL)
RGX_COMMAND_L = r'\((' + RGX_SYMBOL + ')\)'

# Command
RGX_COMMAND_C = r'^(?:([AMD]+)=)?([01\-+ADM&|!]+)(?:;([JMLGNETPQ]{3}))?$'

# Everything that is matched as a comment is deleted
# // *
RGX_COMMENT = r'\/\/.*'


class Parser(object):
    """ Basic parser following the Chapter 6 definitions """

    file_handle = None

    commandType = None
    symbol = None
    constant = None
    dest = None
    comp = None
    jump = None
    line = None

    def __init__(self, assembly_file):
        """ Constructs a parser, opening the file """
        self.file_handle = open(assembly_file)
        self.advance()

    def advance(self):
        """ Reads a line from an open file and updates
            properties about that file.
        """
        if self.file_handle is None:
            raise IOError('Cannot read file further. File closed or EOF')
        self.line = self.file_handle.readline()
        if self.line == '':
            self.file_handle.close()
            self.file_handle = None
        else:
            self._parse_line(self.line)

    def hasMoreCommands(self):
        """ Do we have more commands? """
        return self.file_handle and True

    def _parse_line(self, line:str):
        """ Parses the line, updating properties.
            Does the lifting that advance() claims to do
        """
        self.clear()

        # Remove all whitespace
        line = ''.join(line.split())

        # Remove comments
        line = re.sub(RGX_COMMENT, '', line)
        # Whitespace line. No operation.
        if not line:
            self.commandType = 'NOOP'
            return

        # Matches an Symbol address command
        match = re.match(RGX_COMMAND_A_SYMB, line)
        if match:
            self.commandType = 'A_COMMAND'
            self.symbol = match.group(1)
            return
        match = re.match(RGX_COMMAND_A_CONST, line)
        if match:
            self.commandType = 'A_COMMAND'
            self.constant = int(match.group(1))
            return
        # Matches Label Command
        match = re.match(RGX_COMMAND_L, line)
        if match:
            self.commandType = 'L_COMMAND'
            self.symbol = match.group(1)
            return
        # Matches other commands
        match = re.match(RGX_COMMAND_C, line)
        if match:
            # dest=comp;jump
            self.commandType = 'C_COMMAND'
            self.dest = match.group(1)
            self.comp = match.group(2)
            self.jump = match.group(3)

    def clear(self):
        """ Clear all the properties about the last command """
        self.commandType = None
        self.symbol = None
        self.dest = None
        self.comp = None
        self.jump = None
