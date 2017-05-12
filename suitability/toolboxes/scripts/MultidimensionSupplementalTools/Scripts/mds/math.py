# -*- coding: utf-8 -*-
import datetime
import numpy
import mds.constants


def clamp(
        min_value,
        value,
        max_value):
    """
    Return *value* in case *value* is in the range between *min_value* -
    *max_value* otherwise return either *min_value* or *max_value*
    depending on whether *value* is smaller or larger than the range.
    """
    return max(min_value, min(value, max_value))


def values_to_slice(
        values,
        value1,
        value2):
    """
    Return slice indices corresponding to the location of *value1* and
    *value2* in *values*.

    When slicing *values* using the indices returned, it is guaranteed that
    all values between *value1* and *value2* are included, as well as
    *value1* and *value2* if they are within the the value range of
    *values*. If *value1* and/or *value2* fall outside of *values*' range,
    they are clamped to the extremes of *values*.

    It is assumed that the values in *values* are monotonically increasing
    or decreasing.
    """
    min_value, max_value = (value1, value2) if value1 <= value2 else \
        (value2, value1)
    assert min_value <= max_value
    start_index = -1
    end_index = -1

    if len(values) > 0:
        if values[0] <= values[-1]:
            # Increasing values.
            start_value = clamp(values[0], values[-1], min_value)
            end_value = clamp(values[0], values[-1], max_value)
        else:
            # Decreasing values.
            start_value = clamp(values[-1], values[0], max_value)
            end_value = clamp(values[-1], values[0], min_value)

        start_index = start_index_of_value_in_range(start_value, values)
        end_index = end_index_of_value_in_range(end_value, values)

        assert start_index >= 0 and start_index <= len(values)
        assert end_index >= 0 and end_index <= len(values)

    return (start_index, end_index)


def start_index_of_value_in_range(
        value,
        values):
    """
    Return index of *value* in *values*.

    If *value* is not present in *values* the nearest lower or higher value
    is returned, depending on whether *values* is an increasing or decreasing
    range.

    The idea is that the index can be used as a start index in a slice
    specification and *value* will be included in the slice.
    """
    result = -1
    if len(values) > 0:
        if values[0] <= values[-1]:
            result = start_index_of_value_in_increasing_range(value, values)
        else:
            result = start_index_of_value_in_decreasing_range(value, values)
    return result


def start_index_of_value_in_increasing_range(
        value,
        values):
    result = -1
    # value = max(value, values[0])
    if value <= values[-1]:
        for index in xrange(len(values)):
            if values[index] >= value:
                result = index
                break
    return result


def start_index_of_value_in_decreasing_range(
        value,
        values):
    result = -1
    # value = min(value, values[0])
    if value >= values[-1]:
        for index in xrange(len(values)):
            if values[index] <= value:
                result = index
                break
    return result


def end_index_of_value_in_range(
        value,
        values):
    """
    Return index of the value next to *value* in *values*.

    Whether the next value is higher or lower than *value* depends on whether
    *values* is an increasing or decreasing range.

    The idea is that the index can be used as an end index in a slice
    specification and *value* will be included in the slice.
    """
    result = -1
    if len(values) > 0:
        if values[0] <= values[-1]:
            result = end_index_of_value_in_increasing_range(value, values)
        else:
            result = end_index_of_value_in_decreasing_range(value, values)
    return result


def end_index_of_value_in_increasing_range(
        value,
        values):
    result = -1
    # value = min(values[-1], value)
    if value <= values[-1]:
        for index in xrange(len(values)):
            if values[index] == value:
                result = index + 1
                break
            elif values[index] > value:
                result = index
                break
    return result


def end_index_of_value_in_decreasing_range(
        value,
        values):
    result = -1
    # value = max(values[-1], value)
    if value >= values[-1]:
        for index in xrange(len(values)):
            if values[index] == value:
                result = index + 1
                break
            elif values[index] < value:
                result = index
                break
    return result


def aggregate_per_time_interval(
        time,
        values,
        duration,
        aggregator):
    """
    Aggregate *values* per time *duration*, using *aggregator*.

    time
       Iterable with time points. The time points must be monotonically
       increasing.

    values
       Iterable with numpy arrays with values to aggregate.

    duration
       Length of time within which values are aggregated. It must be possible
       to add *duration* to a time point in *time*.

    aggregator
       Functor to aggregate *values* per *duration*. It will be called with
       one argument: a numpy array with the values to aggregate.

    *values* is an iterable of numpy arrays. This makes it possible to pass
    multiple collections of values. This way, the algorithm only needs to
    pass over the *time* collection once.

    The algorithm divides the time axis in buckets of *duration* length. For
    each collection of values, values are assigned to a bucket and, once all
    values are assigned for a bucket, aggregated.

    The function returns a tuple of two collections. The first is a list of
    time points. These correspond to the start time points of the buckets that
    received values. Empty buckets are skipped. The second collection is a list
    of lists with aggregates per time point.

    The length of the collection of time points returned equals the length of
    each list of values returned, and equals the number of non-empty buckets
    encountered in the inputs.
    """
    assert all([len(time) == len(values[i]) for i in range(len(values))])

    result_time = []
    result_values = [[] for i in xrange(len(values))]

    if len(time) > 0:
        end_index = 0

        while True:
            begin_index = end_index

            # Borders of current period.
            start_time_point = time[begin_index]
            end_time_point = start_time_point + duration

            # Determine index of first time point outside of current period.
            while end_index < len(time):
                if time[end_index] < end_time_point:
                    end_index += 1
                else:
                    break

            # Aggregate values in current period, if any.
            if end_index > begin_index:
                result_time.append(start_time_point)
                for i in xrange(len(values)):
                    result_values[i].append(aggregator(
                        values[i][begin_index:end_index]))

            # Stop if no time points left.
            if end_index == len(time):
                break

    assert len(result_values) == len(values)
    assert all([len(result_values[i]) == len(result_time) for i in xrange(
        len(values))])
    return result_time, result_values


DURATION_BY_TIME_INTERVAL = {
    mds.constants.SECOND: datetime.timedelta(seconds=1),
    mds.constants.MINUTE: datetime.timedelta(minutes=1),
    mds.constants.HOUR: datetime.timedelta(hours=1),
    mds.constants.DAY: datetime.timedelta(days=1),
    # TODO http://labix.org/python-dateutil ?
    mds.constants.JULIAN_DAY: None,
    mds.constants.MONTH: None,
    mds.constants.DECADE: None,
    mds.constants.CENTURY:None
}


def count_per_time_interval(
        time,
        values,
        time_interval,
        ignore_nodata,
        nodata=None):

    def aggregate_ignore_nodata(
            values):
        return (numpy.ones(values.shape[1:], dtype=numpy.uint8) *
            values.shape[0]).tolist()

    def aggregate_dont_ignore_nodata(
            values):
        return numpy.sum(values != nodata, 0)

    aggregate = {
        mds.constants.IGNORE_NODATA: aggregate_ignore_nodata,
        mds.constants.DONT_IGNORE_NODATA: aggregate_dont_ignore_nodata
    }

    result_time, result_values = aggregate_per_time_interval(time, values,
        DURATION_BY_TIME_INTERVAL[time_interval], aggregate[ignore_nodata])

    return result_time, [numpy.array(result_values[i], numpy.min_scalar_type(
        numpy.max(result_values[i]))) for i in xrange(len(result_values))]


def max_per_time_interval(
        time,
        values,
        time_interval,
        ignore_nodata,
        nodata=None):

    def aggregate_ignore_nodata(
            values):
        return numpy.max(values, 0)

    def aggregate_dont_ignore_nodata(
            values):
        return numpy.max(numpy.ma.masked_values(values, nodata), 0)

    aggregate = {
        mds.constants.IGNORE_NODATA: aggregate_ignore_nodata,
        mds.constants.DONT_IGNORE_NODATA: aggregate_dont_ignore_nodata
    }

    result_time, result_values = aggregate_per_time_interval(time, values,
        DURATION_BY_TIME_INTERVAL[time_interval], aggregate[ignore_nodata])

    return result_time, [numpy.array(result_values[i], values[i].dtype) for
        i in xrange(len(result_values))]


def min_per_time_interval(
        time,
        values,
        time_interval,
        ignore_nodata,
        nodata=None):

    def aggregate_ignore_nodata(
            values):
        return numpy.min(values, 0)

    def aggregate_dont_ignore_nodata(
            values):
        return numpy.min(numpy.ma.masked_values(values, nodata), 0)

    aggregate = {
        mds.constants.IGNORE_NODATA: aggregate_ignore_nodata,
        mds.constants.DONT_IGNORE_NODATA: aggregate_dont_ignore_nodata
    }

    result_time, result_values = aggregate_per_time_interval(time, values,
        DURATION_BY_TIME_INTERVAL[time_interval], aggregate[ignore_nodata])

    return result_time, [numpy.array(result_values[i], values[i].dtype) for
        i in xrange(len(result_values))]


def range_per_time_interval(
        time,
        values,
        time_interval,
        ignore_nodata,
        nodata=None):

    def aggregate_ignore_nodata(
            values):
        return numpy.max(values, 0) - numpy.min(values, 0)

    def aggregate_dont_ignore_nodata(
            values):
        return numpy.max(numpy.ma.masked_values(values, nodata), 0) - \
            numpy.min(numpy.ma.masked_values(values, nodata), 0)

    aggregate = {
        mds.constants.IGNORE_NODATA: aggregate_ignore_nodata,
        mds.constants.DONT_IGNORE_NODATA: aggregate_dont_ignore_nodata
    }

    result_time, result_values = aggregate_per_time_interval(time, values,
        DURATION_BY_TIME_INTERVAL[time_interval], aggregate[ignore_nodata])

    return result_time, [numpy.array(result_values[i], values[i].dtype) for
        i in xrange(len(result_values))]


def mean_per_time_interval(
        time,
        values,
        time_interval,
        ignore_nodata,
        nodata=None):

    def aggregate_ignore_nodata(
            values):
        return numpy.mean(values, 0)

    def aggregate_dont_ignore_nodata(
            values):
        return numpy.mean(numpy.ma.masked_values(values, nodata), 0)

    aggregate = {
        mds.constants.IGNORE_NODATA: aggregate_ignore_nodata,
        mds.constants.DONT_IGNORE_NODATA: aggregate_dont_ignore_nodata
    }

    result_time, result_values = aggregate_per_time_interval(time, values,
        DURATION_BY_TIME_INTERVAL[time_interval], aggregate[ignore_nodata])

    return result_time, [numpy.array(result_values[i], numpy.float64) for
        i in xrange(len(result_values))]


def std_per_time_interval(
        time,
        values,
        time_interval,
        ignore_nodata,
        nodata=None):

    def aggregate_ignore_nodata(
            values):
        return numpy.std(values, 0)

    def aggregate_dont_ignore_nodata(
            values):
        return numpy.std(numpy.ma.masked_values(values, nodata), 0)

    aggregate = {
        mds.constants.IGNORE_NODATA: aggregate_ignore_nodata,
        mds.constants.DONT_IGNORE_NODATA: aggregate_dont_ignore_nodata
    }

    result_time, result_values = aggregate_per_time_interval(time, values,
        DURATION_BY_TIME_INTERVAL[time_interval], aggregate[ignore_nodata])

    return result_time, [numpy.array(result_values[i], numpy.float64) for
        i in xrange(len(result_values))]


def sum_per_time_interval(
        time,
        values,
        time_interval,
        ignore_nodata,
        nodata=None):

    def aggregate_ignore_nodata(
            values):
        return numpy.sum(values, 0)

    def aggregate_dont_ignore_nodata(
            values):
        return numpy.sum(numpy.ma.masked_values(values, nodata), 0)

    aggregate = {
        mds.constants.IGNORE_NODATA: aggregate_ignore_nodata,
        mds.constants.DONT_IGNORE_NODATA: aggregate_dont_ignore_nodata
    }

    result_time, result_values = aggregate_per_time_interval(time, values,
        DURATION_BY_TIME_INTERVAL[time_interval], aggregate[ignore_nodata])

    return result_time, [numpy.array(result_values[i], values[i].dtype) for
        i in xrange(len(result_values))]


def aggregate_over_time_interval(
        time,
        values,
        time_point_to_id,
        aggregator):
    """
    Aggregate *values* over time, using *aggregator*.

    time
       Iterable with time points. The time points must be monotonically
       increasing.

    values
       Iterable with numpy arrays with values to aggregate.

    time_point_to_id
       Functor to translate time point to id. A time point id is a number that
       represents the time point. Possible examples:
       - Hour of day: 3PM has id 15
       - Day of year: January 5th has id 5
       - Month of year: March has id 3
       The mapping between time point and id doesn't matter to the algorithm
       and is determined by the caller. It is important that the same hour,
       day, or month on different days, months, or years respectively, have
       the same corresponding time point id.

    aggregator
       Functor to aggregate *values* per *duration*. It will be called with
       one argument: a numpy array with the values to aggregate.

    *values* is an iterable of numpy arrays. This makes it possible to pass
    multiple collections of values. This way, the algorithm only needs to
    pass over the *time* collection once.

    The algorithm creates a new time axis, containing the ids of the
    time points that are present in *time*. For each collection of values,
    values are assigned to a time point id and, once all values are assigned
    to a time point id, aggregated.

    The function returns a tuple of two collections. The first is the list of
    time point ids. The second collection is a list of lists with aggregates
    per time point.

    The length of the collection of time points returned equals the length of
    each list of values returned, and equals the number of unique time point
    ids.
    """
    assert all([len(time) == len(values[i]) for i in range(len(values))])

    # List with time point ids.
    time_point_ids = [time_point_to_id(time[i]) for i in xrange(len(time))]

    # Dictionary with per time point id a list. This list contains for each
    # list in *values* another list. This list contains for each time point
    # id an empty list. This last list will recieve values from *values*.
    # Afterwords, these lists will be aggregated to single values per time
    # points.
    result = {
        # For each time point id...
        #   and for each array in values...
        #     an empty list.
        time_point_id: [[] for i in xrange(len(values))] for time_point_id in
            time_point_ids
    }

    for i in xrange(len(time)):
        time_point_id = time_point_to_id(time[i])
        for j in xrange(len(values)):
            result[time_point_id][j].append(values[j][i])

    for time_point_id in result:
        result[time_point_id] = [aggregator(numpy.array(
            result[time_point_id][i], dtype=values[i].dtype)) for i in \
                xrange(len(values))]

    result_time = result.keys()
    result_values = [[] for i in xrange(len(values))]

    for i in xrange(len(values)):
        result_values[i] = [result[time_point_id][i] for time_point_id in
            result]

    return result_time, result_values


TIME_POINT_TO_ID_BY_TIME_INTERVAL = {
   mds.constants.HOUR_OF_DAY: lambda time_point: time_point.time().hour,
   mds.constants.JULIAN_DAY_OF_YEAR: lambda time_point: \
       (time_point - datetime.datetime(time_point.year, 1, 1)).days + 1,
   mds.constants.MONTH_OF_YEAR: lambda time_point: time_point.date().month
}


def count_over_time_interval(
        time,
        values,
        time_interval,
        ignore_nodata,
        nodata=None):

    def aggregate_ignore_nodata(
            values):
        return (numpy.ones(values.shape[1:], dtype=numpy.uint8) *
            values.shape[0]).tolist()

    def aggregate_dont_ignore_nodata(
            values):
        return numpy.sum(values != nodata, 0)

    aggregate = {
        mds.constants.IGNORE_NODATA: aggregate_ignore_nodata,
        mds.constants.DONT_IGNORE_NODATA: aggregate_dont_ignore_nodata
    }

    result_time, result_values = aggregate_over_time_interval(time, values,
        TIME_POINT_TO_ID_BY_TIME_INTERVAL[time_interval],
        aggregate[ignore_nodata])

    return result_time, [numpy.array(result_values[i], numpy.min_scalar_type(
        numpy.max(result_values[i]))) for i in xrange(len(result_values))]


def max_over_time_interval(
        time,
        values,
        time_interval,
        ignore_nodata,
        nodata=None):

    def aggregate_ignore_nodata(
            values):
        return numpy.max(values, 0)

    def aggregate_dont_ignore_nodata(
            values):
        return numpy.max(numpy.ma.masked_values(values, nodata), 0)

    aggregate = {
        mds.constants.IGNORE_NODATA: aggregate_ignore_nodata,
        mds.constants.DONT_IGNORE_NODATA: aggregate_dont_ignore_nodata
    }

    result_time, result_values = aggregate_over_time_interval(time, values,
        TIME_POINT_TO_ID_BY_TIME_INTERVAL[time_interval],
        aggregate[ignore_nodata])

    return result_time, [numpy.array(result_values[i], values[i].dtype) for
        i in xrange(len(result_values))]


def min_over_time_interval(
        time,
        values,
        time_interval,
        ignore_nodata,
        nodata=None):

    def aggregate_ignore_nodata(
            values):
        return numpy.min(values, 0)

    def aggregate_dont_ignore_nodata(
            values):
        return numpy.min(numpy.ma.masked_values(values, nodata), 0)

    aggregate = {
        mds.constants.IGNORE_NODATA: aggregate_ignore_nodata,
        mds.constants.DONT_IGNORE_NODATA: aggregate_dont_ignore_nodata
    }

    result_time, result_values = aggregate_over_time_interval(time, values,
        TIME_POINT_TO_ID_BY_TIME_INTERVAL[time_interval],
        aggregate[ignore_nodata])

    return result_time, [numpy.array(result_values[i], values[i].dtype) for
        i in xrange(len(result_values))]


def range_over_time_interval(
        time,
        values,
        time_interval,
        ignore_nodata,
        nodata=None):

    def aggregate_ignore_nodata(
            values):
        return numpy.max(values, 0) - numpy.min(values, 0)

    def aggregate_dont_ignore_nodata(
            values):
        return numpy.max(numpy.ma.masked_values(values, nodata), 0) - \
            numpy.min(numpy.ma.masked_values(values, nodata), 0)

    aggregate = {
        mds.constants.IGNORE_NODATA: aggregate_ignore_nodata,
        mds.constants.DONT_IGNORE_NODATA: aggregate_dont_ignore_nodata
    }

    result_time, result_values = aggregate_over_time_interval(time, values,
        TIME_POINT_TO_ID_BY_TIME_INTERVAL[time_interval],
        aggregate[ignore_nodata])

    return result_time, [numpy.array(result_values[i], values[i].dtype) for
        i in xrange(len(result_values))]


def mean_over_time_interval(
        time,
        values,
        time_interval,
        ignore_nodata,
        nodata=None):

    def aggregate_ignore_nodata(
            values):
        return numpy.mean(values, 0)

    def aggregate_dont_ignore_nodata(
            values):
        return numpy.mean(numpy.ma.masked_values(values, nodata), 0)

    aggregate = {
        mds.constants.IGNORE_NODATA: aggregate_ignore_nodata,
        mds.constants.DONT_IGNORE_NODATA: aggregate_dont_ignore_nodata
    }

    result_time, result_values = aggregate_over_time_interval(time, values,
        TIME_POINT_TO_ID_BY_TIME_INTERVAL[time_interval],
        aggregate[ignore_nodata])

    return result_time, [numpy.array(result_values[i], numpy.float64) for
        i in xrange(len(result_values))]


def std_over_time_interval(
        time,
        values,
        time_interval,
        ignore_nodata,
        nodata=None):

    def aggregate_ignore_nodata(
            values):
        return numpy.std(values, 0)

    def aggregate_dont_ignore_nodata(
            values):
        return numpy.std(numpy.ma.masked_values(values, nodata), 0)

    aggregate = {
        mds.constants.IGNORE_NODATA: aggregate_ignore_nodata,
        mds.constants.DONT_IGNORE_NODATA: aggregate_dont_ignore_nodata
    }

    result_time, result_values = aggregate_over_time_interval(time, values,
        TIME_POINT_TO_ID_BY_TIME_INTERVAL[time_interval],
        aggregate[ignore_nodata])

    return result_time, [numpy.array(result_values[i], numpy.float64) for
        i in xrange(len(result_values))]


def sum_over_time_interval(
        time,
        values,
        time_interval,
        ignore_nodata,
        nodata=None):

    def aggregate_ignore_nodata(
            values):
        return numpy.sum(values, 0)

    def aggregate_dont_ignore_nodata(
            values):
        return numpy.sum(numpy.ma.masked_values(values, nodata), 0)

    aggregate = {
        mds.constants.IGNORE_NODATA: aggregate_ignore_nodata,
        mds.constants.DONT_IGNORE_NODATA: aggregate_dont_ignore_nodata
    }

    result_time, result_values = aggregate_over_time_interval(time, values,
        TIME_POINT_TO_ID_BY_TIME_INTERVAL[time_interval],
        aggregate[ignore_nodata])

    return result_time, [numpy.array(result_values[i], values[i].dtype) for
        i in xrange(len(result_values))]


def aggregator(
        statistics_type,
        time_interval):
    assert statistics_type in mds.constants.STATISTICS_TYPES.values(), \
        statistics_type
    assert time_interval in mds.constants.TIME_INTERVALS.values(), time_interval
    assert (time_interval in mds.constants.WITHIN_TIME_INTERVALS) ^ \
        (time_interval in mds.constants.OVER_TIME_INTERVALS)

    result = None
    if statistics_type == mds.constants.COUNT:
        if time_interval in mds.constants.WITHIN_TIME_INTERVALS:
            result = count_per_time_interval
        else:
            result = count_over_time_interval
    elif statistics_type == mds.constants.MAX:
        if time_interval in mds.constants.WITHIN_TIME_INTERVALS:
            result = max_per_time_interval
        else:
            result = max_over_time_interval
    elif statistics_type == mds.constants.MEAN:
        if time_interval in mds.constants.WITHIN_TIME_INTERVALS:
            result = mean_per_time_interval
        else:
            result = mean_over_time_interval
    elif statistics_type == mds.constants.MIN:
        if time_interval in mds.constants.WITHIN_TIME_INTERVALS:
            result = min_per_time_interval
        else:
            result = min_over_time_interval
    elif statistics_type == mds.constants.RANGE:
        if time_interval in mds.constants.WITHIN_TIME_INTERVALS:
            result = range_per_time_interval
        else:
            result = range_over_time_interval
    elif statistics_type == mds.constants.STD:
        if time_interval in mds.constants.WITHIN_TIME_INTERVALS:
            result = std_per_time_interval
        else:
            result = std_over_time_interval
    elif statistics_type == mds.constants.SUM:
        if time_interval in mds.constants.WITHIN_TIME_INTERVALS:
            result = sum_per_time_interval
        else:
            result = sum_over_time_interval

    assert result
    return result
