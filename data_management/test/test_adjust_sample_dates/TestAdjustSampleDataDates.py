#------------------------------------------------------------------------------
# Copyright 2015 Esri
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
# TestAdjustSampleDataDates.py
# Description: Test Adjust Sample Daa Dates Toolbox
# Requirements: ArcGIS Desktop Standard
# ----------------------------------------------------------------------------

import arcpy
import sys
import traceback
import TestUtilities
import os
import datetime

class LicenseError(Exception):
    ''' '''
    pass

def createFeatureSet():
    ''' create in-memory features '''
    sr = arcpy.SpatialReference(4326)
    fc = arcpy.CreateFeatureclass_management("in_memory", "tempfc", "POINT",
                                             None, "DISABLED", "DISABLED",
                                             sr)[0]
    arcpy.AddField_management(fc, "datetimestart", "DATE",)
    fields = ["SHAPE@XY", "datetimestart"]
    rows = arcpy.da.InsertCursor(fc, fields)
    pnt = arcpy.Point(0.0, 0.0)
    dtValue = datetime.datetime(2000,01,01,00,00,00)
    for x in range(0, 100):
        rows.insertRow([pnt, dtValue])
    del rows
    return fc

def getFieldBefore(fc):
    ''' get date/time field values before '''
    datetimeStart = {}
    beforeRows = arcpy.da.SearchCursor(fc, ["OID@", "datetimestart"])
    for row in beforeRows:
        datetimeStart[row[0]] = row[1]
    del beforeRows
    return datetimeStart

def appendFieldAfter(fc,datetimeStart):
    ''' add the date/time field values after the change '''
    afterRows = arcpy.da.SearchCursor(fc, ["OID@", "datetimestart"])
    for row in afterRows:
        before = datetimeStart[row[0]]
        after = row[1]
        datetimeStart[row[0]] = [before,after]
    return datetimeStart

try:
    print("Importing toolbox... ")
    arcpy.ImportToolbox(TestUtilities.toolbox,"ajdustdates")
    arcpy.env.overwriteOutput = True

    #Set tool param variables
    print("Creating feature set... ")
    inputFeatures = createFeatureSet()

    # get 'datetimestart' field values and OIDs
    # {<OID>:[<before>,<after>]}
    print("getting 'before' dates... ")
    checkDates = getFieldBefore(inputFeatures)

    #Testing
    arcpy.AddMessage("Running tool: Change Sample Data Dates to Recent Dates")
    arcpy.ChangeSampleDataDatestoRecentDates_ajdustdates(inputFeatures)

    # get list of 'datetimestart' after tool run
    print("getting 'after' dates... ")
    checkDates = appendFieldAfter(inputFeatures, checkDates)

    # compare before and after values and report OIDs that are haven't changed or are NULL
    print("Comparing values... ")
    foundError = False
    for key in checkDates.keys():
        vals = checkDates[key]
        before, after = vals[0], vals[1]
        if after == None:
            print("OID " + str(key) + " has value NONE and was not updated: " + str(vals))
            foundError = True
        if before == after:
            print("OID " + str(key) + " value has not changed and was not updated: " + str(vals))
            foundError = True
        else:
            print("OID " + str(key) + " OK: " + str(vals))

    if foundError == True:
        raise "Date/time update failed!!!"

    print("Test Passed")

except arcpy.ExecuteError: 
    # Get the arcpy error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    print(msgs)

    # return a system error code
    sys.exit(-1)

except:
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
    print(pymsg + "\n")
    print(msgs)

    # return a system error code 
    sys.exit(-1)
    