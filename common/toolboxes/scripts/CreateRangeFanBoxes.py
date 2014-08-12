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
# RangeFanByBearingLimits.py
# CreateRangeFanBoxes: Common objects/methods used by test scripts
# Requirements: ArcGIS Desktop Standard
# -----------------------------------------------------------------------------

# IMPORTS ==========================================
import os, sys, math, traceback
import arcpy
from arcpy import env
from arcpy import da


# ARGUMENTS & LOCALS ===============================
deleteme = []
debug = False

inputFeatures = arcpy.GetParameterAsText(0)
outputExtentBoxes = arcpy.GetParameterAsText(1)
outputWeaponPositions = arcpy.GetParameterAsText(2)


# CONSTANTS ========================================
GCS_WGS_1984 = arcpy.SpatialReference(r"WGS 1984")


# FUNCTIONS ========================================
def Geo2Arithmetic(inAngle):
    outAngle = -1.0
    if (inAngle > 360.0):
        inAngle = math.fmod(inAngle,360.0)
    
    # if 360, make it zero
    if inAngle == 360.0: inAngle = 0.0
    
    #0 to 90
    if (inAngle >= 0.0 and inAngle <= 90.0):
        outAngle = math.fabs(inAngle - 90.0)
    
    # 90 to 360
    if (inAngle > 90.0 and inAngle < 360.0):
        outAngle = 360.0 - (inAngle - 90.0)
        
    return outAngle


try:
    # Create output, use input as template for SR    
    inputFeaturesDesc = arcpy.Describe(inputFeatures)    
    inputFeaturesShapeName = inputFeaturesDesc.shapeFieldName
    inputFeaturesOID = inputFeaturesDesc.oidFieldName
    inputFeatureSR = inputFeaturesDesc.spatialReference
    
    scratch = env.scratchWorkspace

    outputExtentBoxes = arcpy.CreateFeatureclass_management(os.path.dirname(outputExtentBoxes),os.path.basename(outputExtentBoxes),"POLYGON","#","DISABLED","DISABLED",inputFeatureSR)
    arcpy.AddField_management(outputExtentBoxes,"RFID","LONG")
    arcpy.AddField_management(outputExtentBoxes,"Bearing","DOUBLE")
    arcpy.AddField_management(outputExtentBoxes,"Range","DOUBLE")
    arcpy.AddField_management(outputExtentBoxes,"Width","DOUBLE")
    arcpy.AddField_management(outputExtentBoxes,"LeftAz","DOUBLE")
    arcpy.AddField_management(outputExtentBoxes,"RightAz","DOUBLE")
    arcpy.AddField_management(outputExtentBoxes,"WeaponX","DOUBLE")
    arcpy.AddField_management(outputExtentBoxes,"WeaponY","DOUBLE")
    outputExtentBoxesOID = arcpy.Describe(outputExtentBoxes).oidFieldName
    

    # start the cursors
    searchRows = arcpy.da.SearchCursor(inputFeatures,["OID@","SHAPE@","Bearing","Range","LeftAz","RightAz"])
    writeRows = arcpy.da.InsertCursor(outputExtentBoxes,["SHAPE@","RFID","Bearing","Range","Width","LeftAz","RightAz","WeaponX","WeaponY"])
    # for each range fan in the inputFeatures    
    for currentRead in searchRows:
        # read current range fan points
        currentReadID = currentRead[0]
        arcpy.AddMessage("Building box for range fan OID " + str(currentReadID))
        partCoordList = []
        for part in currentRead[1]:
            for pnt in part:
                partCoordList.append(arcpy.Point(pnt.X,pnt.Y))
                
        # get critical points
        startPoint = partCoordList[0] # first point
        secondPoint = partCoordList[1] # second point
        n2Point = partCoordList[len(partCoordList) - 2] # second-to-last point
        
        # get range fan properties
        fanRange = currentRead[3]
        width = math.sqrt(math.pow(secondPoint.X - n2Point.X,2) + math.pow(secondPoint.Y - n2Point.Y,2))
        halfWidth = width / 2.0
        if debug == True: arcpy.AddMessage("range,width: " + str(fanRange) + "," + str(width))
        
        # get orientation bearings
        bearing = currentRead[2]
        leftAz = currentRead[4]
        rightAz = currentRead[5]
        bearingDegrees = bearing
        
        backBearing = 0.0
        if bearing < 180.0:
            backBearing = 360.0 + (bearing - 180.0)
        else:
            backBearing = bearing - 180.0
            
        leftBearing = 0.0
        if bearing < 90.0:
            leftBearing = 360.0 + (bearing - 90.0)
        else:
            leftBearing = bearing - 90.0
            
        rightBearing = 0.0
        if bearing > 270.0:
            rightBearing = math.fabs(360.0 - (bearing + 90.0))
        else:
            rightBearing = bearing + 90.0
        
        if debug == True: arcpy.AddMessage("bearing,left,right,back: " + str(bearing) + "," + str(leftBearing) + "," + str(rightBearing) + "," + str(backBearing))
        
        
        # find box coordinates
        boxArray = arcpy.Array()      
        
        # from start point go half width by crossbearing
        llX =  startPoint.X + (halfWidth * math.cos(math.radians(Geo2Arithmetic(leftBearing))))
        llY =  startPoint.Y + (halfWidth * math.sin(math.radians(Geo2Arithmetic(leftBearing))))
        llPoint = arcpy.Point(llX,llY)
        boxArray.add(llPoint)
        
        # from llPoint go fanRange by bearing
        ulX = llPoint.X + (fanRange * math.cos(math.radians(Geo2Arithmetic(bearing))))
        ulY = llPoint.Y + (fanRange * math.sin(math.radians(Geo2Arithmetic(bearing))))
        ulPoint = arcpy.Point(ulX,ulY)
        boxArray.add(ulPoint)        
        
        # from ulPoint go width by negative crossbearing
        urX = ulPoint.X + (width * math.cos(math.radians(Geo2Arithmetic(rightBearing))))
        urY = ulPoint.Y + (width * math.sin(math.radians(Geo2Arithmetic(rightBearing))))
        urPoint = arcpy.Point(urX,urY)
        boxArray.add(urPoint)
        
        # from urPoint go fanRange by negative bearing
        lrX = urPoint.X + (fanRange * math.cos(math.radians(Geo2Arithmetic(backBearing))))
        lrY = urPoint.Y + (fanRange * math.sin(math.radians(Geo2Arithmetic(backBearing))))
        lrPoint = arcpy.Point(lrX,lrY)
        boxArray.add(lrPoint)        
        
        # take point array and make a polygon
        boxArray.add(llPoint)               
        boxPolygon = arcpy.Polygon(boxArray)

        # write row to output featureclass: ["SHAPE@"],"RFID","Bearing","Range","Width","LeftAz","RightAz","WeaponX","WeaponY'   
        writeRows.insertRow([boxPolygon,currentReadID,bearing,fanRange,width,leftAz,rightAz,startPoint.X,startPoint.Y])
    
    # release cursors
    del searchRows
    del writeRows
    
    # Get Weapon Position as points
    arcpy.AddMessage("Finding weapon position MGRS ...")
    arcpy.MakeXYEventLayer_management(outputExtentBoxes,"WeaponX","WeaponY","XYEvent",inputFeatureSR)
    arcpy.CopyFeatures_management("XYEvent",outputWeaponPositions)
    tempGeoPoints = os.path.join(scratch,"tempGeoPoints")
    deleteme.append(tempGeoPoints)
    arcpy.Project_management(outputWeaponPositions,tempGeoPoints,GCS_WGS_1984)
    arcpy.AddXY_management(tempGeoPoints)
    tempCCNPoints = os.path.join("in_memory","tempCCNPoints")
    deleteme.append(tempCCNPoints)
    arcpy.ConvertCoordinateNotation_management(tempGeoPoints,tempCCNPoints,"POINT_X","POINT_Y","DD_2","MGRS","RFID",GCS_WGS_1984)
    arcpy.JoinField_management(outputWeaponPositions,"RFID",tempCCNPoints,"RFID",["MGRS"])
    
    # ENHANCEMENT: add Range Rings for each weapon position 
    
    # set script output parameter
    arcpy.SetParameter(1,outputExtentBoxes)
    arcpy.SetParameter(2,outputWeaponPositions)


except arcpy.ExecuteError: 
    # Get the tool error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    print msgs

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
    print pymsg + "\n"
    print msgs

finally:
    # cleanup intermediate datasets
    if debug == True: arcpy.AddMessage("Removing intermediate datasets...")
    for i in deleteme:
        if debug == True: arcpy.AddMessage("Removing: " + str(i))
        arcpy.Delete_management(i)
    if debug == True: arcpy.AddMessage("Done")