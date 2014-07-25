#------------------------------------------------------------------------------
# Copyright 2013 Esri
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


import os, sys, traceback, math, decimal
import arcpy
from arcpy import env

input_centers = arcpy.GetParameterAsText(0)
numberOfRings = int(arcpy.GetParameterAsText(1))
ringInterval = float(arcpy.GetParameterAsText(2))
outputRings = arcpy.GetParameterAsText(3)
distanceUnits = arcpy.GetParameterAsText(4)
numberOfRadials = int(arcpy.GetParameterAsText(5))
bearingUnits = arcpy.GetParameterAsText(6)
outputRadials = arcpy.GetParameterAsText(7)
buildRadials = True
delete_me = []

try:
    currentOverwriteOutput = env.overwriteOutput
    env.overwriteOutput = True
    installInfo = arcpy.GetInstallInfo("desktop")
    installDirectory = installInfo["InstallDir"]
    GCS_WGS_1984 = os.path.join(installDirectory,r"Coordinate Systems", r"Geographic Coordinate Systems", r"World",r"WGS 1984.prj")
    
    # Get SR of Input Centers
    inputCentersSR = arcpy.Describe(input_centers).spatialReference
    if inputCentersSR == "" or inputCentersSR == None :
        inputCentersSR = GCS_WGS_1984    
    
    result = arcpy.GetCount_management(input_centers)
    arcpy.AddMessage("Using " + str(result) + " centers ...")
    
    # create temp table
    tempTable = os.path.join(env.scratchWorkspace,"tempTable")
    delete_me.append(tempTable)
    arcpy.CreateTable_management(os.path.dirname(tempTable),os.path.basename(tempTable))
    arcpy.AddField_management(tempTable,"POINT_X","DOUBLE")
    arcpy.AddField_management(tempTable,"POINT_Y","DOUBLE")
    arcpy.AddField_management(tempTable,"Range","DOUBLE")
    arcpy.AddField_management(tempTable,"RingID","LONG")
    arcpy.AddField_management(tempTable,"RingRadius","DOUBLE")
    
    # if zero radials, don't build them
    if numberOfRadials < 1: buildRadials = False
    
    # Add XY
    arcpy.AddXY_management(input_centers)
    
    # build ring values
    arcpy.AddMessage("Building ring table ...")
    getRows = arcpy.SearchCursor(input_centers)
    addRows = arcpy.InsertCursor(tempTable)
    y = 1
    for getRow in getRows:
        pointX = getRow.POINT_X
        pointY = getRow.POINT_Y
        x = 1
        while x <= numberOfRings:
           addRow = addRows.newRow()
           addRow.POINT_X = pointX
           addRow.POINT_Y = pointY
           rd = float(x) * ringInterval
           #print "row: " + str(x) + " " + str(pointX) + " " + str(pointY) + " " + str(rd)
           addRow.Range = rd
           addRow.RingRadius = rd * 2.0
           addRow.RingID = y
           addRows.insertRow(addRow)
           x += 1
        y += 1
    del addRow 
    del addRows
    del getRow
    del getRows
    
    results = arcpy.GetCount_management(tempTable)
    
    # build ellipses
    arcpy.AddMessage("Constructing " + str(results) + " ring features ...")
    arcpy.TableToEllipse_management(tempTable,outputRings,"POINT_X","POINT_Y","RingRadius","RingRadius",distanceUnits,"#","#","#",inputCentersSR)
    
    # Join fields
    tempTableOIDFieldName = arcpy.Describe(tempTable).OIDFieldName
    ringOIDFieldName = arcpy.Describe(outputRings).OIDFieldName
    arcpy.JoinField_management(outputRings,ringOIDFieldName,tempTable,tempTableOIDFieldName,["Range","RingID"])
    
    # Delete junk field
    arcpy.DeleteField_management(outputRings,"RingRadius")

    
    # create radials temp table
    if buildRadials == True:
        arcpy.AddMessage("Using " + str(numberOfRadials) + " radials ...")
        tempRadialTable = os.path.join(env.scratchWorkspace,"tempRadialTable")
        delete_me.append(tempRadialTable)
        arcpy.CreateTable_management(os.path.dirname(tempRadialTable),os.path.basename(tempRadialTable))
        arcpy.AddField_management(tempRadialTable,"POINT_X","DOUBLE")
        arcpy.AddField_management(tempRadialTable,"POINT_Y","DOUBLE")
        arcpy.AddField_management(tempRadialTable,"Azimuth","DOUBLE")
        arcpy.AddField_management(tempRadialTable,"Range","DOUBLE")
        arcpy.AddField_management(tempRadialTable,"RingID","LONG")
        
        maxRadialRange = ringInterval * numberOfRings
        radialInterval = 360.0/numberOfRadials
        radialList = []
        r = 1
        while r <= numberOfRadials:
            radialList.append(r * radialInterval)
            r += 1
        
        arcpy.AddMessage("Building radial table ...")
        getRows = arcpy.SearchCursor(input_centers)
        addRows = arcpy.InsertCursor(tempRadialTable)
        y = 1
        for getRow in getRows:
            pointX = getRow.POINT_X
            pointY = getRow.POINT_Y
            for radialAzimuth in radialList:
                addRow = addRows.newRow()
                addRow.POINT_X = pointX
                addRow.POINT_Y = pointY
                addRow.Range = maxRadialRange
                addRow.Azimuth = radialAzimuth
                addRow.RingID = y
                addRows.insertRow(addRow)
            y += 1
        del addRow 
        del addRows
        del getRow
        del getRows
        
        results = arcpy.GetCount_management(tempRadialTable)
        
        # build ellipses
        arcpy.AddMessage("Constructing " + str(results) + " radial features ...")
        arcpy.BearingDistanceToLine_management(tempRadialTable,outputRadials,"POINT_X","POINT_Y","Range",distanceUnits,"Azimuth",bearingUnits,"RHUMB_LINE","RingID",inputCentersSR)
        
        # Join fields
        tempRadialTableOIDFieldName = arcpy.Describe(tempRadialTable).OIDFieldName
        radialOIDFieldName = arcpy.Describe(outputRadials).OIDFieldName
        #arcpy.JoinField_management(outputRadials,radialOIDFieldName,tempRadialTable,tempRadialTableOIDFieldName,["Azimuth","Range","RingID"])
        
    else:
        arcpy.AddMessage("Zero radials to build ...")
    
    
    # set output
    arcpy.SetParameter(3,outputRings)
    if buildRadials == True:
        arcpy.SetParameter(7,outputRadials)

    # cleanup
    arcpy.AddMessage("Removing scratch datasets:")
    for ds in delete_me:
        arcpy.AddMessage(str(ds))
        arcpy.Delete_management(ds)
    
    env.overwriteOutput = currentOverwriteOutput
    
except arcpy.ExecuteError:
    error = True
    # Get the tool error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    print msgs

except:
    # Get the traceback object
    error = True
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    # Return python error messages for use in script tool or Python Window
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)

    # Print Python error messages for use in Python / Python Window
    print pymsg + "\n"
    print msgs
    
    