# -*- coding: utf-8 -*-
import collections


class OrderedSet(collections.MutableSet):
    """
    An ordered set is a set in which the order of the elements added to the
    set is maintained. The order of elements added multiple times is
    not changed, unless they are removed from the set first.
    """

    def __init__(self,
            iterable=[]):
        # The ordered dict maintains the order of the elements and makes sure
        # the elements are unique.
        self.elements = collections.OrderedDict()
        for element in iterable:
            self.elements[element] = True

    def __repr__(self):
        return "OrderedSet({})".format(repr(self.elements.keys()))

    def __str__(self):
        return "OrderedSet({})".format(str(self.elements.keys()))

    def __contains__(self,
            element):
        """
        As per Container.
        """
        return element in self.elements

    def __iter__(self):
        """
        As per Iterable.
        """
        return self.elements.iterkeys()

    def __len__(self):
        """
        As per Sized.
        """
        return len(self.elements)

    def add(self,
            element):
        """
        As per MutableSet.
        """
        self.elements[element] = True

    def discard(self,
            element):
        """
        As per MutableSet.
        """
        if element in self.elements:
            del self.elements[element]

    def __eq__(self,
            other):
        """
        Order of the elements is relevant. If the two sets contain the same
        elements, but they are ordered differently, then these sets don't
        compare equal.
        """
        if len(self) != len(other):
            return False
        else:
            iter1 = iter(self)
            iter2 = iter(other)
            for element1 in iter1:
                element2 = iter2.next()
                if element1 != element2:
                    return False
        return True

    def __ne__(self,
            other):
        return not (self == other)


def order(
        set_to_order,
        ordered_set):
    """
    Return a copy of *set_to_order* where all values are in the same order as
    in *ordered_set*.

    *set_to_order* must be a subset of *ordered_set*.
    """
    assert isinstance(set_to_order, collections.Set)
    assert all([value in ordered_set for value in set_to_order])
    result = OrderedSet()
    for value in ordered_set:
        if value in set_to_order:
            result.add(value)
    assert len(result) == len(set_to_order)
    return result
