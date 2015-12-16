# -*- coding: utf-8 -*-
from coordinate import *
from coards import *
from cf import *
from conventions import *
from generic import *


CONVENTION_CLASSES = [
    CF,
    Coards,
    Coordinate
]
"""
Classes that implement a netcdf convention.
"""


def select_convention(
        dataset,
        filter_out_nd_coordinates,
        favor_class=None):
    """
    Return a Convention specialization that implements the conventions used in
    *dataset*.

    filter_out_nd_coordinates
        Most coordinate variables are one-dimensional. If this argument is
        True, data variables depending on more-dimensional coordinate
        variables are filtered out. A reason for this may be that your
        application doesn't support such variables.

    favor_class
        In case *dataset* adheres to multiple supported conventions and
        *favor_class* is one of them, then it is used. Otherwise
        :py:class:`Conventions` is used.

    In case *dataset* doesn't adhere to a supported convention,
    :py:class:`Generic` is used. Supported conventions are listed in
    :py:data:`CONVENTION_CLASSES`.
    """
    assert favor_class is None or favor_class in CONVENTION_CLASSES, favor_class
    conventions = []
    for convention_class in CONVENTION_CLASSES:
        if convention_class.conforms(dataset):
            conventions.append(convention_class(dataset,
                filter_out_nd_coordinates))

    result = None
    if len(conventions) == 0:
        # Dataset doesn't adhere to one of the supported conventions.
        result = Generic(dataset, filter_out_nd_coordinates)
    elif len(conventions) == 1:
        # Dataset adheres to exactly one supported convention.
        result = conventions[0]
    else:
        # Dataset adheres to more than one supported convention.
        if favor_class is not None and favor_class in [type(convention) for
                convention in conventions]:
            # Select the favored convention.
            result = favor_class(dataset, filter_out_nd_coordinates)
        else:
            # Use all conventions.
            result = Conventions(dataset, filter_out_nd_coordinates,
                conventions)

    return result
