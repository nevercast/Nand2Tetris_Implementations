# coding=utf-8
""" Parses Assembly lines and provides information about them """
import re
import asyncio


# Matches Alpha-Numeric, $, . and :
# The first letter cannot be decimal.
RGX_SYMBOL = r'[a-zA-Z$.:][\w$.:]+'

# @SYMBOL
RGX_COMMAND_A_SYMB = r'@(?P<symbol>' + RGX_SYMBOL + ')'

# @CONSTANT
RGX_COMMAND_A_CONST = r'@(?P<constant>\d+)'

# (SYMBOL)
RGX_COMMAND_L = r'\((?P<symbol>' + RGX_SYMBOL + ')\)'

# Command
RGX_COMMAND_C = r'^(?:(?P<destination>[AMD]+)=)?(?P<compute>[01\-+ADM&|!]+)(?:;(?P<jump>[JMLGNETPQ]{3}))?$'

# Everything that is matched as a comment is deleted
# // *
RGX_COMMENT = r'\/\/.*'


class ParserLine(object):
    """ A line that has been hit by the parser """

    def __init__(self, line, line_type):
        self.line = line
        self.line_type = line_type
        self.attributes = {}

    line = None
    line_type = None  # 'load_symbol', 'load_constant', 'compute', 'label'

    attributes = {}
    destination = None  # Destination for compute operation
    computation = None  # Compute operation subtype
    jump_condition = None  # Jump condition
    constant = None
    symbol = None


class Parser(object):
    """ Basic parser following the Chapter 6 definitions """

    def __init__(self, assembly_file):
        """ Constructs a parser, opening the file """
        self.file_handle = open(assembly_file)

        self.parser_mapping = {}
        self.add_mapping(RGX_COMMAND_A_SYMB, 'load_symbol')
        self.add_mapping(RGX_COMMAND_A_CONST, 'load_constant')
        self.add_mapping(RGX_COMMAND_L, 'label')
        self.add_mapping(RGX_COMMAND_C, 'compute')

    def add_mapping(self, regex, type):
        compiled = re.compile(regex)
        self.parser_mapping[compiled] = type

    @asyncio.coroutine
    def parse(self):
        while self.file_handle:
            line = self.file_handle.readline()
            if line == '':
                self.file_handle = None
                return
            yield from self._parse_line(line)

    @asyncio.coroutine
    def _parse_line(self, line:str):
        """ Parses the line, updating properties.
        """

        line = self.strip_line(line)
        if not line:
            return

        for regex, parameters in self.parser_mapping.items():
            match = regex.match(line)
            if match:
                line_data = ParserLine(line=line, line_type=parameters[0])
                parameters[1](line_data, match)
                yield line_data

    @staticmethod
    def _a_command_symbol(parser_line: ParserLine, match):
        parser_line.symbol = match.group(1)

    @staticmethod
    def _a_command_constant(parser_line: ParserLine, match):
        parser_line.constant = int(match.group(1))

    @staticmethod
    def _c_command(parser_line: ParserLine, match):
        parser_line.destination = match.group(1)
        parser_line.computation = match.group(2)
        parser_line.jump_condition = match.group(3)

    @staticmethod
    def strip_line(line):
        """ Strip whitespace and comments """
        # Remove all whitespace
        line = ''.join(line.split())

        # Remove comments
        line = re.sub(RGX_COMMENT, '', line)
        return line
