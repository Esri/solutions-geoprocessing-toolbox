# -*- coding: utf-8 -*-
import collections


class Keyword(
    collections.namedtuple("Keyword", ["id", "name"])):
    """
    Class for representing keywords. Keywords have a name and an id. The actual
    value of the id attribute is not relevant and is only used in comparisons.
    The value should not be dependent upon.
    """

    def __eq__(self,
            keyword):
        # Default equality implementation compares the id and the name. This
        # is faster.
        return self.id == keyword.id

    def __ne__(self,
            keyword):
        # Default inequality implementation compares the id and the name. This
        # is faster.
        return self.id != keyword.id
