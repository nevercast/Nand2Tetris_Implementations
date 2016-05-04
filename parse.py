# coding=utf-8
""" Parses Assembly lines and provides information about them """
import re
import asyncio
import softobject


# Matches Alpha-Numeric, $, . and :
# The first letter cannot be decimal.
RGX_SYMBOL = r'[a-zA-Z$.:][\w$.:]+'

# @SYMBOL
RGX_COMMAND_A_SYMB = r'@(?P<symbol>' + RGX_SYMBOL + ')'

# @CONSTANT
RGX_COMMAND_A_CONST = r'@(?P<constant_int>\d+)'

# (SYMBOL)
RGX_COMMAND_L = r'\((?P<symbol>' + RGX_SYMBOL + ')\)'

# Command
RGX_COMMAND_C = r'^(?:(?P<destination>[AMD]+)=)?(?P<compute>[01\-+ADM&|!]+)(?:;(?P<jump>[JMLGNETPQ]{3}))?$'

# Everything that is matched as a comment is deleted
# // *
RGX_COMMENT = r'\/\/.*'


class ParserLine(softobject.SoftObject):
    """ A line that has been hit by the parser """

    line = None
    line_type = None  # 'load_symbol', 'load_constant', 'compute', 'label'

    def __init__(self, line, line_type):
        self.line = line
        self.line_type = line_type


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

    def add_mapping(self, regex, command_type):
        compiled = re.compile(regex)
        self.parser_mapping[compiled] = command_type

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

        for regex, line_type in self.parser_mapping.items():
            match = regex.match(line)
            if match:
                line_data = ParserLine(line=line, line_type=line_type)
                for group, value in match.groupdict().items():
                    if '_' in group:
                        identifier, type_filter = group.split('_', maxsplit=2)
                        if type_filter == 'int':
                            value = int(value)
                        else:
                            raise RuntimeError('Unsupported type filter {} for group {}'.format(type_filter. group))
                    else:
                        identifier = group
                    setattr(line_data, identifier, value)
                yield line_data

    @staticmethod
    def strip_line(line):
        """ Strip whitespace and comments """
        # Remove all whitespace
        line = ''.join(line.split())

        # Remove comments
        line = re.sub(RGX_COMMENT, '', line)
        return line
