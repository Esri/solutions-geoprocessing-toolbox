# -*- coding: utf-8 -*-
import netCDF4


def _units(
        variable):
    assert hasattr(variable, "units")

    # Don't lowercase this value. The casing is relevant.
    units = variable.units

    # netcdf4-python expects milliseconds, while some datasets provide msecs.
    units = units.replace("msecs", "milliseconds")

    return units


def _calendar(
        variable):
    return variable.calendar.lower() if hasattr(variable, "calendar") else \
        "standard"


def coordinates_to_dates(
        coordinates,
        variable):
    """
    Convert *coordinates* to dates (datetime.datetime instances), given the
    units and calendar attribute values of *variable*.

    The *variable* passed in must be the time variable. It must have a units
    attribute. If it doesn't have a calendar attribute, 'standard' is used as
    the default calendar.

    The *coordinates* passed in can be a single value or a list of values.
    """
    units = _units(variable)
    calendar = _calendar(variable)
    return netCDF4.num2date(coordinates, units, calendar)


def dates_to_coordinates(
        dates,
        variable):
    """
    Convert *dates* (datetime.datetime instances) to coordinates, given the
    units and calendar attribute values of *variable*.

    The *variable* passed in must be the time variable. It must have a units
    attribute. If it doesn't have a calendar attribute, 'standard' is used as
    the default calendar.

    The *dates* passed in can be a single value or a list of values.
    """
    units = _units(variable)
    calendar = _calendar(variable)
    return netCDF4.date2num(dates, units, calendar)

