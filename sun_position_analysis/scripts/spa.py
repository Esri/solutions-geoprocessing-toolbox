#------------------------------------------------------------------------------
# Copyright 2014 Esri
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------
# spa.py
# Description: Sun Position and Hillshade
# Requirements: ArcGIS Desktop Standard
#------------------------------------------------------------------------------


# IMPORTS ==========================================
import os, sys, math, traceback, types, datetime, time
import arcpy
from arcpy import env
from arcpy import sa
from arcpy.sa import *
from time import mktime, gmtime, strftime

timezone = {
    '(UTC-12:00) International Date Line West': -12,
    '(UTC-11:00) Midway Island, Samoa': -11,
    '(UTC-10:00) Hawaii': -10,
    '(UTC-9:00) Alaska': -9,
    '(UTC-8:00) Pacific Time (US & Canada), Baja California': -8,
    '(UTC-7:00) Mountain Time (US & Canada), Chihuahua, La Paz, Mazatlan': -7,
    '(UTC-6:00) Central Time (US & Canada), Central America, Guadalajara,'\
    ' Mexico City': -6,
    '(UTC-5:00) Eastern Time (US & Canada), Bogota, Lima, Quito': -5,
    '(UTC-4:00) Atlantic Time (Canada), Santiago, La Paz, San Juan': -4,
    '(UTC-3:30) Newfoundland (Canada)': -3.5,
    '(UTC-3:00) Brasilia, Buenos Aires, Cayenne, Greenland, Montevideo': -3,
    '(UTC-2:00) Mid-Atlantic': -2,
    '(UTC-1:00) Cape Verde Islands, Azores': -1,
    '(UTC) Casablanca, Dublin, Edinburgh, London, Monrovia': 0,
    '(UTC+1:00) West Central Africa, Amsterdam, Berlin, Rome, Sarajevo,'\
    ' Stockholm': 1,
    '(UTC+2:00) Amman, Athens, Beirut, Cairo, Harare, Helsinki, Istanbul,'\
    ' Pretoria': 2,
    '(UTC+3:00) Kuwait, Baghdad, Moscow, Nairobi, Riyadh': 3,
    '(UTC+3:30) Tehran': 3.5,
    '(UTC+4:00) Abu Dhabi, Baku, Muscat, Tbilisi, Yerevan': 4,
    '(UTC+4:30) Afghanistan': 4.5,
    '(UTC+5:00) Ekaterinburg. Islamabad, Karachi, Tashkent': 5,
    '(UTC+5:30) Chennai, Kolkata, Mumbai, New Delhi': 5.5,
    '(UTC+6:00) Astana, Dhaka, Novosibirsk': 6,
    '(UTC+7:00) Bangkok, Hanoi, Jakarta': 7,
    '(UTC+8:00) Beijing, Hong Kong, Kuala Lampur, Singapore, Taipei,'\
    ' Ulaanbaatar': 8,
    '(UTC+9:00) Osaka, Seoul, Tokyo, Yakutsk': 9,
    '(UTC+9:30) Adelaide, Darwin': 9.5,
    '(UTC+10:00) Brisbane, Melbourne, Guam, Bladivostok': 10,
    '(UTC+11:00) Magadan, Solomon Islands': 11,
    '(UTC+12:00) Fiji, Marshall Islands': 12
            }
class MissingParameterError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# Represents the position of the sun on a given date at a given observer point
class SunPosition:
    def __init__(self, date, point, azimuth, altitude):
        self.date = date
        self.point = point
        self.azimuth = azimuth
        self.altitude = altitude

# Given a featureclass, determines the centerpoint
def CenterPoint(fc):

    if debug == True:
        arcpy.AddMessage("Determining centerpoint of featureclass: " + fc)

    aoiCenter = os.path.join(env.scratchGDB,"aoiCenter")
    deleteme.append(aoiCenter)
    arcpy.FeatureToPoint_management(fc, aoiCenter, "CENTROID")
    shapeName = arcpy.Describe(aoiCenter).shapeFieldName

    if debug == True:
        arcpy.AddMessage("Shapefield Name: " + shapeName)

    # Get the centerpoint and project on the fly to WGS84 due to the calculations
    # used by the Sun Position algorithm (lat/lon required)
    rows = arcpy.SearchCursor(aoiCenter, "", GCS_WGS_1984, shapeName)
    #row = rows.next() #UPDATE
    row = next(rows)
    geom = row.getValue(shapeName)
    point = geom.getPart()

    if debug == True:
        arcpy.AddMessage("Centerpoint (x,y): " + str(point.X) + ", " + str(point.Y))

    return point

#Returns the Julian day number of a date.
def date_to_julian_day(my_date):
    a = (14 - my_date.month)//12
    y = my_date.year + 4800 - a
    m = my_date.month + 12*a - 3
    return my_date.day + ((153*m + 2)//5) + 365*y + y//4 - y//100 + y//400 - 32045

# Given a datetime and a observation point, determine the position of the sun
def CalculateSunPosition(date, observerPoint):

    if debug == True:
        arcpy.AddMessage("Determining sun position for date: " + str(date))

    twoPi = math.pi * 2
    lat = observerPoint.Y
    lon = observerPoint.X

    if debug == True:
        arcpy.AddMessage("lat: " + str(lat))
        arcpy.AddMessage("lon: " + str(lon))

    # Determine the the day in the year (i.e. 123rd, 345th, 366th, etc...) on which the requested date falls
    timetuple = date.timetuple()
    tempHour = timetuple.tm_hour + (timetuple.tm_min / 60) + (timetuple.tm_sec/3600)
    julianDate = date_to_julian_day(date)
    time = julianDate - 2451545.0

    # Ecliptic coordinates

    # Mean Longitude
    mnlong = 280.460 + .9856474 * time
    mnlong = mnlong % 360
    if mnlong < 0:
        mnlong += 360

    # Mean Anomaly
    mnanom = 357.528 + .9856003 * time
    mnanom = mnanom % 360
    if mnanom < 0:
        mnanom += 360
    mnanom = math.radians(mnanom)

    # Ecliptic longitude and obliquity of ecliptic
    eclong = mnlong + 1.915 * math.sin(mnanom) + 0.020 * math.sin(2*mnanom)
    eclong = eclong % 360
    if eclong<0:
        eclong += 360
    oblqec = 23.439 - 0.0000004 * time
    eclong = math.radians(eclong)
    oblqec = math.radians(oblqec)

    # Celestial Coordinates
    # Right ascension and declination
    num = math.cos(oblqec) * math.sin(eclong)
    den = math.cos(eclong)
    ra = math.atan(num / den)
    if den < 0:
        ra += math.pi

    if den >= 0 and num < 0:
        ra += twoPi
    dec = math.asin(math.sin(oblqec) * math.sin(eclong))

    # Local coordinates
    # Greenwich mean sidereal time
    gmst = 6.697375 + .0657098242 * time + tempHour
    gmst = gmst % 24
    if gmst < 0:
        gmst += 24

    # Local mean sidereal time
    lmst = gmst + lon / 15
    lmst = lmst % 24
    if lmst < 0:
        lmst += 24
    lmst = lmst * 15.0
    lmst = math.radians(lmst)

    # Hour angle
    ha = lmst - ra
    if ha < (-math.pi):
        ha += twoPi
    if ha > math.pi:
        ha -= twoPi

    # Latitude to Radians
    latRad = math.radians(lat)

    # Solar zenith angle amd Azimuth
    zenithAngle = math.acos(math.sin(latRad) * math.sin(dec) + math.cos(latRad) * math.cos(dec) * math.cos(ha))
    az = math.acos(((math.sin(latRad) * math.cos(zenithAngle)) - math.sin(dec)) / (math.cos(latRad) * math.sin(zenithAngle)))

    # Elevation
    el = math.asin(math.sin(dec) * math.sin(latRad) + math.cos(dec) * math.cos(latRad) * math.cos(ha))

    if debug == True:
        arcpy.AddMessage("dec: " + str(dec))
        arcpy.AddMessage("latRad: " + str(latRad))
        arcpy.AddMessage("ha: " + str(ha))

    # For logic and names, see Spencer, J.W. 1989 Solar Energy.  42(4):353
    cosAzPos = ( 0 <= (math.sin(dec) - math.sin(el) * math.sin(lat)) )
    sinAzNeg = ( math.sin(az) < 0 )

    if debug == True:
        arcpy.AddMessage("Calculated Elevation Radians: " + str(el))
    if debug == True:
        arcpy.AddMessage("Calculated Azimuth Radians: " + str(az))

    el = math.degrees(el)
    az = math.degrees(az)

    if ha > 0:
        az = az + 180
    else:
        az = 540 - az
    az = az % 360

    if debug == True:
        arcpy.AddMessage("Calculated Elevation Degrees: " + str(el))
    if debug == True:
        arcpy.AddMessage("Calculated Azimuth Degrees: " + str(az))

    sp = SunPosition(date,observerPoint,az,el)
    return sp

# Check out any necessary licenses
arcpy.CheckOutExtension("Spatial")

# Globals
deleteme = []
debug = False

# WGS84 Spatial Reference
sr = arcpy.SpatialReference()
sr.factoryCode = 4326
sr.create()
GCS_WGS_1984 = sr

## Web Mercator
#sr = arcpy.SpatialReference()
#sr.factoryCode = 3857
#sr.create()
#webMercator = sr

# Local variables:

# Script arguments
inputAOI = arcpy.GetParameterAsText(0)
if inputAOI == '#' or not inputAOI:
    raise MissingParameterError("inputAOI")

inputElevation = arcpy.GetParameterAsText(1)
if inputElevation == '#' or not inputElevation:
    raise MissingParameterError("inputElevation")

inputDatetime = arcpy.GetParameterAsText(2)
if inputDatetime == '#' or not inputDatetime:
    raise MissingParameterError("inputDatetime")

inputTimezone = arcpy.GetParameterAsText(3)
if inputTimezone == '#' or not inputTimezone:
    raise MissingParameterError("inputTimezone")

outputHillshade = arcpy.GetParameterAsText(4)
if outputHillshade == '#' or not outputHillshade:
    raise MissingParameterError("outputHillshade")

# Configure the Environment
env.cellSize = inputElevation
env.extent = inputAOI
env.mask = inputAOI
env.snapRaster = inputElevation
env.overwriteOutput = True
env.resample = "CUBIC"
env.compression = "LZ77"
env.rasterStatistics = 'STATISTICS'

try:

    # Datetime comes in looking like this: 11/1/2013 3:26:37 PM
    # Convert the string to a datetime object
    timeStruct = time.strptime(inputDatetime, "%m/%d/%Y %I:%M:%S %p")
    utcoffset = time.timezone
    if time.daylight > 0:
        utcoffset = time.altzone

    # Adjust to UTC time to run the calculations
    dt = datetime.datetime.fromtimestamp(mktime(timeStruct))
    if debug == True:
        arcpy.AddMessage("Initially provided date time (" + inputTimezone + "): " + str(dt))
    dt = dt - datetime.timedelta(seconds=(timezone[inputTimezone]*60*60))
    if debug == True:
        arcpy.AddMessage("UTC-adjusted date time: " + str(dt))

    # Get the centerpoint of the input AOI to use as the observer position
    if debug == True:
        arcpy.AddMessage("Generating observer centerpoint...")

    centerPoint = CenterPoint(inputAOI)

    if debug == True:
        arcpy.AddMessage("Determining Sun Position")

    sunPosition = CalculateSunPosition(dt,centerPoint)

    # From the observer position, and the provided date time, determine the sun angle and altitude

    if sunPosition.altitude < 0:
        if debug == True:
            arcpy.AddMessage("Generating constant raster...")
        outConstRaster = CreateConstantRaster(0, "INTEGER")
        outConstRaster.save(outputHillshade)
    else:
        if debug == True:
            arcpy.AddMessage("Generating hillshade...")
        tempHillshade = arcpy.sa.Hillshade(inputElevation, sunPosition.azimuth, sunPosition.altitude, "NO_SHADOWS")
        tempHillshade.save(outputHillshade)

    if debug == True:
        arcpy.AddMessage("Calculating hillshade statistics...")

    arcpy.CalculateStatistics_management(outputHillshade)

except arcpy.ExecuteError:
    if debug == True:
        arcpy.AddMessage("CRASH: " + str(time.strftime("%m/%d/%Y  %H:%M:%S", time.localtime())))
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    arcpy.AddError("Traceback: " + tbinfo)
    # Get the tool error messages
    msgs = arcpy.GetMessages()
    arcpy.AddError(msgs)
    #print msgs #UPDATE
    print(msgs)
except MissingParameterError as e:
    if debug == True:
        arcpy.AddMessage("CRASH: " + str(time.strftime("%m/%d/%Y  %H:%M:%S", time.localtime())))
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    arcpy.AddError("Traceback: " + tbinfo)
    # Get the tool error messages
    msg = e.value + " parameter is missing."
    arcpy.AddError(msg)
    #print msg #UPDATE
    print (msg)
except:
    if debug == True:
        arcpy.AddMessage("CRASH: " + str(time.strftime("%m/%d/%Y  %H:%M:%S", time.localtime())))
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    # Return python error messages for use in script tool or Python Window
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)

    # Print Python error messages for use in Python / Python Window
    #print pymsg + "\n" #UPDATE
    #print msgs #UPDATE
    print ((pymsg + "\n"))
    print (msgs)
finally:

    arcpy.CheckInExtension("Spatial")
    # cleanup intermediate datasets
    if debug == True: arcpy.AddMessage("Removing intermediate datasets...")
    for i in deleteme:
        if debug == True: arcpy.AddMessage("Removing: " + str(i))
        if arcpy.Exists(i):
            arcpy.Delete_management(i)
            pass
    if debug == True: arcpy.AddMessage("Done")