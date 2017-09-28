# -*- coding: utf-8 -*-
import mds.keyword
import mds.keywords


SELECT_BY_VALUE = 1
"""
Boundary coordinate values are interpreted as coordinate values. These values
correspond to the values stored in the dataset.

The value of this constant is not relevant. Assume it will be changed.
"""

SELECT_BY_INDEX = 2
"""
Boundary coordinate values are interpreted as indices. These indices correspond
with positions of coordinate values stored in the dataset, with the index of
the first coordinate value being 0.

The value of this constant is not relevant. Assume it will be changed.
"""


# Keyword constants. Each keyword has a unique name and id.
COUNT, MAX, MEAN, MIN, RANGE, STD, SUM = (
    mds.keyword.Keyword(*enum) for enum in enumerate([
        "COUNT", "MAX", "MEAN", "MIN", "RANGE", "STD", "SUM"]))

STATISTICS_TYPES = mds.keywords.Keywords([
    COUNT,
    MAX,
    MEAN,
    MIN,
    RANGE,
    STD,
    SUM
])
"""
Statistics types supported by the temporal aggregation code.
"""

# Keyword constants. Each keyword has a unique name and id.
SECOND, MINUTE, HOUR, DAY, JULIAN_DAY, MONTH, YEAR, DECADE, CENTURY, \
    HOUR_OF_DAY, JULIAN_DAY_OF_YEAR, MONTH_OF_YEAR = (
        mds.keyword.Keyword(*enum) for enum in enumerate([
            "SECOND", "MINUTE", "HOUR", "DAY", "JULIAN DAY", "MONTH", "YEAR",
            "DECADE", "CENTURY", "HOUR OF DAY", "JULIAN DAY OF YEAR",
            "MONTH OF YEAR"]))

TIME_INTERVALS = mds.keywords.Keywords([
    SECOND,
    MINUTE,
    HOUR,
    DAY,
    JULIAN_DAY,
    MONTH,
    YEAR,
    DECADE,
    CENTURY,
    HOUR_OF_DAY,
    JULIAN_DAY_OF_YEAR,
    MONTH_OF_YEAR
])
"""
Time intervals supported by the temporal aggregation code.
"""


WITHIN_TIME_INTERVALS = [
    SECOND,
    MINUTE,
    HOUR,
    DAY,
    JULIAN_DAY,
    MONTH,
    YEAR,
    DECADE,
    CENTURY
]


OVER_TIME_INTERVALS = [
    HOUR_OF_DAY,
    JULIAN_DAY_OF_YEAR,
    MONTH_OF_YEAR
]


# Keyword constants. Each keyword has a unique name and id.
IGNORE_NODATA, DONT_IGNORE_NODATA = (
    mds.keyword.Keyword(*enum) for enum in enumerate([
        "IGNORE_NODATA", "DONT_IGNORE_NODATA"]))
