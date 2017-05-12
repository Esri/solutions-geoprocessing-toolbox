# -*- coding: utf-8 -*-


class Keywords(dict):

    def __init__(self,
            keywords=[]):
        for keyword in keywords:
            self.__setitem__(keyword.name, keyword)

    # def __iter__(self):
    #     return self.itervalues()
