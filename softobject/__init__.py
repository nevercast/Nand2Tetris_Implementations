# coding=utf-8
""" Javascripty objects """

class SoftObject(object):

    def __getattr__(self, item):
        """ Makes object attributes soft """
        return self.__dict__.setdefault(item, None)