# -*- coding: utf-8 -*-
import datetime
import re


class TimezoneInfo(datetime.tzinfo):

    def __init__(self,
            offset):
        self.offset = offset

    def utcoffset(self,
            dt):
        return datetime.timedelta(minutes=self.offset)

    def dst(self,
            dt):
        return None

    def tzname(self,
            dt):
        return None


def from_iso_format(
        string):
    """
    Parse a string representing the date and time in ISO 8601 format,
    YYYY-MM-DDTHH:MM:SS.mmmmmm or, if microsecond is 0, YYYY-MM-DDTHH:MM:SS

    If utcoffset() does not return None, a 6-character string is appended,
    giving the UTC offset in (signed) hours and minutes:
    YYYY-MM-DDTHH:MM:SS.mmmmmm+HH:MM or, if microsecond is 0
    YYYY-MM-DDTHH:MM:SS+HH:MM
    """
    # Regex and strptime patterns.
    patterns = [
        (
            # 2013-03-19 13:03:10.123456
            r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{0,6}$",
            "%Y-%m-%d %H:%M:%S.%f"
        ),
        (
            # 2013-03-19 13:03:10
            r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$",
            "%Y-%m-%d %H:%M:%S"
        )
    ]

    result = None

    for regex_pattern, strptime_pattern in patterns:
        match = re.match(regex_pattern, string)

        if match:
            result = datetime.datetime.strptime(string, strptime_pattern)
            break
        elif len(string) >= 6:
            # strptime doesn't support parsing timezone offsets, so we have to
            # parse it ourselves.
            timezone = string[-6:]

            # +HH:MM or -HH:MM
            if re.match(r"[+-]\d{2}:\d{2}$", timezone):
                # Good, matched timezone info.
                match = re.match(regex_pattern, string[:-6])

                if match:
                    # Good, the rest of the string contains the date/time info.
                    result = datetime.datetime.strptime(string[:-6],
                        strptime_pattern)

                    # Convert timezone offset to minutes.
                    offset_hours = int(timezone[0:3])
                    offset_minutes = int(timezone[4:6])
                    if offset_hours < 0:
                        offset_minutes *= -1
                    offset_minutes += offset_hours * 60

                    # Create new instance with correct timezone offset info.
                    result = result.replace(tzinfo=TimezoneInfo(offset_minutes))
                    break

    if not result:
        raise ValueError("String not in ISO 8601 format")

    assert result, string
    return result


def to_iso_format(
        date_time):
    """
    Return a string representing the date and time in ISO 8601 format,
    YYYY-MM-DD HH:MM:SS.mmmmmm or, if microsecond is 0, YYYY-MM-DD HH:MM:SS

    If utcoffset() does not return None, a 6-character string is appended,
    giving the UTC offset in (signed) hours and minutes:
    YYYY-MM-DD HH:MM:SS.mmmmmm+HH:MM or, if microsecond is 0
    YYYY-MM-DD HH:MM:SS+HH:MM
    """
    return date_time.isoformat(sep=" ")
