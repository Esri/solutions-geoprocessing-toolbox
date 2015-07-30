ProcessMetar.py - NOAA Metar Aggregated Live Feed routine v1.0.2
----------------------------------------------------------------

The ProcessMetar.py Python script is an Aggregated Live Feed routine
designed to decode and record Metar report data to a local esri File
Geodatabase Featureclass. This FileGDB can then be used by ArcGIS
Mapping clients directly or it can be served as a Map Service using
ArcGIS Server. The final deployment of the live FileGDB is up to you.
Just review the Configuration File and change as required. Maybe you
want to zip up the contents and push to some remote server or upload to
Amazon's S3 environment.

Use the accompanying 'ProcessMetar.cfg' configuration file to alter
default behavior or output details.

This script can be used to replace a local FileGDB copy of the most
recent full-cycle of Metar data, or it can be used to update a local
FileGDB copy of the current-cycle of Metar data. The full-cycle contains
every station that reported in the last hourly cycle. And the current-
cycle contains only the stations that have reported thus far this hour.

The current-cycle is more up to date, but may not contain all reports.
The full-cycle contains all reports, but the data can be more than an
hour old.

To maintain a general list of all reports that are fairly current, run
this script once an hour, as is. This will replace the local FileGDB
each run.

To maintain a complete list of all reports that are as current as
possible. Change the 'updateUsingCurrentCycle' setting in the config
file to 'True' and run this script at least once every quarter hour.
This will update the contents of the local FileGDB with the current
content.

Storage Layout:
---------------

<Home>
|   ALFlib.py           (can be stored elsewhere, see importPath option)
|   MetarDecoder.py     (can be stored elsewhere, see importPath option)
|   ProcessMetar.cfg
|   ProcessMetar.py
+---LiveData           (can be located anywhere, see configuration file)
|   |   WindSpeedDirection.lyr     (sample Map Layer file for Live data)
|   \---Metar.gdb
|           <Geodatabase Files>
+---Logs               (can be located anywhere, see configuration file)
|   |   CurrentMetar_<YYYYMM>.txt        (Summary of activity for month)
|   |   CurrentMetar_LastRun.txt                  (Details for Last Run)
|   \---CurrentMetar_Errors
|           <YYYYMMDD_HHMI>.txt      (Details for Run if error detected)
\---Work               (can be located anywhere, see configuration file)
    \---Metar.gdb
            <Geodatabase Files>

Process Workflow:
-----------------

- Read 'ProcessMetar.cfg' file, set options
- Setup/Manage Logging, handled by 'ALFlib.py'
- Import ArcPy and other components
- Decode Metar data, handled by 'MetarDecoder.py'
- Prepare workspace
- Write/Update data
- Invoke Deployment logic found in configuration file

Command-line usage:
-------------------

Simply enter 'ProcessMetar.py' from a command-line console to launch.

Depenancies:
------------

This script relies on:
- esri ArcGIS 10.0+, ArcPy
- ALFlib.py v1.0.1+ helper script
- MetarDecoder.py v1.0.1+ helper script
