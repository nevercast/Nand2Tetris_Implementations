# coding=utf-8
""" Generic line parser"""
import re
import asyncio
import softobject


class ParserLine(softobject.SoftObject):
    """ A line that has been hit by the parser """

    line = None
    line_type = None

    def __init__(self, line, line_type):
        self.line = line
        self.line_type = line_type


class Parser(object):
    """ Basic parser following the Chapter 6 definitions """

    def __init__(self, assembly_file):
        """ Constructs a parser, opening the file """
        self.file_handle = open(assembly_file)

        self.parser_mapping = {}
        self.type_filters = {}
        self.transformers = {}
        self.add_type_filter('int', int)

    def add_mapping(self, regex, command_type):
        compiled = re.compile(regex)
        self.parser_mapping[compiled] = command_type

    def add_type_filter(self, type_name, pred):
        self.type_filters[type_name] = pred

    def add_transformer(self, select_re, transform_re):
        if isinstance(select_re, str):
            select_re = re.compile(select_re)
        self.transformers[select_re] = transform_re

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

        line = self.transform_line(line)
        if not line:
            return

        for regex, line_type in self.parser_mapping.items():
            match = regex.match(line)
            if match:
                line_data = ParserLine(line=line, line_type=line_type)
                for group, value in match.groupdict().items():
                    if '_' in group:
                        identifier, type_filter = group.split('_', maxsplit=2)
                        if type_filter in self.type_filters:
                            value = self.type_filters[type_filter](value)
                        else:
                            raise RuntimeError('Unsupported type filter {} for group {}'.format(type_filter. group))
                    else:
                        identifier = group
                    setattr(line_data, identifier, value)
                yield line_data

    def transform_line(self, line):
        """ Run transformers """
        for transform_selector, transform in self.transformers.items():
            line = re.sub(transform_selector, transform, line)
        return line
