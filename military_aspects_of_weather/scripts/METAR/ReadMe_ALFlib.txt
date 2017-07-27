ALFlib.py - Read Me for Aggregated Live Feed library v1.1.0
-----------------------------------------------------------

The ALFlib.py script is a Python 'Helper' script that includes Classes
and Functions that, when 'import'ed, are designed to be used by other
Python scripts to help re-use common code and speed script development.

This script can be placed along side the scripts that imports it, but
ideally, you should store it in a common script folder used to store
other multi-use scripts, like the Python lib folder. The system Path
varilable can include this folder name or, for best results, the script
that imports these common scripts should issue a 'sys.path.append( <path>)'
instruction to update the path location before importing said scripts.
It's up to you!

Command-line usage/help:
------------------------

This script can be launched from the command-line to view the more
specific help details for each Class or Function. Simply enter
'ALFlib.py -h [name]' from a command-line console to see the detialed
help. Include the Class or Function 'name' to see specific item details.

Library version details:
------------------------
ALFlib.major : Major release number
ALFlib.minor : Minor release number
ALFlib.bug : Bug fix level for release
ALFlib.desc : Description details

Available as of v1.1.0, invoke the 'minVersion' function from your script
to verify that the version of this library meets the minimum version
requirements for your script. This will return a True or False result.

Current Classes include:
------------------------

AppLock : (Added v1.1.0, May 2012) Creates and manages a temporary Lock
          file. Allowing scipts to control whether they limit execution
          to a single instance or multiple (parallel) instances.
Constants : Contains a collection of general use constants, lists, and
            dictionaries.
CountryCodeLoader : Manages a cache file stored in the system temp
                    folder, which contains Country Code to name cross
                    reference details.
Logger : Manages log file generation and archiving automatically for
         any Python script that instantiates it.
WeatherStationLoader : Manages a cache file stored in the system temp
                       folder, which contains the world wide weather
                       station details.

Current Functions include:
--------------------------

c2f : Converts celsius degrees to fahrenheit.
dms2dd : Converts angular Degrees, Minutes, Seconds, and Bearing to
         decimal degrees.
f2c : Converts fahrenheit degrees to celsius.
heatIndex : Calculates the current heat index in celsius from the
            current temperature and humidity.
minVersion : (Added v1.1.0, May 2012) Reports True if the version of
             this library is at least the minimum specified by the
             input provided. False otherwise.
relativeHumidity : Calculates the current relative humidity as Percent
                   from the current celsius temperature and dewpoint.
version : Reports the version details for this script.
windChill : Calculates the current wind chill factor in celsius from
            the current celsius temperature and wind speed.
