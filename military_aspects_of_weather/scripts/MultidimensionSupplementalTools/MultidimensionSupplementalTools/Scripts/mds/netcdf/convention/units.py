# -*- coding: utf-8 -*-
import numpy


def is_length(
        units):
    return units in [
        "kilometer", "kilometers", "km",
        "meter", "meters", "m",
        "centimeter", "centimeters", "cm",
        "decimeter", "decimeters", "dm",
        "feet", "ft"
    ]

def is_longitude(
        units):
    return units in [
        "degrees_east",
        "degree_east",
        "degree_E",
        "degrees_E",
        # Not recommended, but allowed.
        "degrees_west",
        "degree_west",
        "degree_W",
        "degrees_W"
    ]

def is_latitude(
        units):
    return units in [
        "degrees_north",
        "degree_north",
        "degree_N",
        "degrees_N"
        # These are not mentioned in the COARDS specification.
        # "degrees_south",
        # "degree_south",
        # "degree_S",
        # "degrees_S"
    ]

def is_space(
        units):
    return is_longitude(units) or units.is_latitude(units)

def is_time(
        units):
    return units.find(" since ") != -1

def is_numeric(
        data_type):
    assert isinstance(data_type, numpy.dtype)  # As per netcdf4-python docs.
    return issubclass(data_type.type, numpy.number)
