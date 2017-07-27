MetarDecoder.py - Read Me for NOAA Metar Report Decoder v1.0.2
--------------------------------------------------------------

The MetarDecoder.py Python script reads and decodes the current NOAA
National Weather Service 'METeorological Aerodrome Reports' received
from equipment located at airports, military installations, and weather
stations around the world. It stores the decoded values in an internal
dictionary that can be accessed by the script that instantiates it.

This script can be placed along side the scripts that import it, but
ideally, you should store it in a common script folder used to store
other multi-use scripts. The system Path varilable can include this
folder name or, for best results, the script that imports these common
scripts should issue a 'sys.path.append( <path>)' instruction to update
the path location before importing said scripts.

Command-line usage/help:
------------------------

This script can be launched from the command-line to view the more
specific help details or to perform live decoding. Simply enter
'MetarDecoder.py -h' from a command-line console to see the detialed
help.

Depenancies:
------------

This script relies on the 'ALFlib.py' v1.0.1+ helper script.
