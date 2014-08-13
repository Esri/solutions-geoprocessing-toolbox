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
# RangeFan.py
# Description: Create Range Fan
# Requirements: ArcGIS Desktop Standard
# -----------------------------------------------------------------------------

# IMPORTS ==========================================
import os, sys, math, traceback
import arcpy
from arcpy import env


# CONSTANTS ========================================
gravitationalConstant = 9.80665 # meters/second^2, approx. 32.174 ft/sec^2


# FUNCTIONS ========================================
def Geo2Arithmetic(inAngle):
    inAngle = math.fmod(inAngle,360.0)
    #0 to 90
    if (inAngle >= 0.0 or inAngle <= 90.0):
        outAngle = math.fabs(inAngle - 90.0)
    
    # 90 to 360
    if (inAngle >= 90.0 or inAngle < 360.0):
        outAngle = 360.0 - (inAngle - 90.0)

    return float(outAngle)


# ARGUMENTS & LOCALS ===============================
argCount = arcpy.GetArgumentCount()

inFeature = arcpy.GetParameterAsText(0)
dRange = float(arcpy.GetParameterAsText(1)) #1000.0 # meters
bearing = float(arcpy.GetParameterAsText(2)) #45.0 # degrees
traversal = float(arcpy.GetParameterAsText(3)) #60.0 # degrees
outFeature = arcpy.GetParameterAsText(4)
outputCoordinateSystem = arcpy.GetParameterAsText(5)
    
deleteme = []
debug = True
leftAngle = 0.0 # degrees
rightAngle = 90.0 # degrees
WGS84 = arcpy.SpatialReference(r"WGS 1984")
WebMercator = arcpy.SpatialReference(r"WGS 1984 Web Mercator (Auxiliary Sphere)")
if (outputCoordinateSystem == "") or (outputCoordinateSystem is None) :
    # if the output coordinate system is empty we need to use a default projected CS
    outputCoordinateSystem = WebMercator
else:
    #The script is passed a string representation of the output coordinate system, load it into a spatial ref object here
    sr = arcpy.SpatialReference()
    sr.loadFromString(outputCoordinateSystem)
    outputCoordinateSystem = sr
if debug == True: arcpy.AddMessage("output coordinate system: " + str(outputCoordinateSystem.name))

try:

    currentOverwriteOutput = env.overwriteOutput
    env.overwriteOutput = True
    installInfo = arcpy.GetInstallInfo("desktop")
    installDirectory = installInfo["InstallDir"]
    env.overwriteOutput = True
    scratch = env.scratchWorkspace
    
    prjInFeature = os.path.join(scratch,"prjInFeature")
    arcpy.AddMessage("Projecting input points to " + str(outputCoordinateSystem.name) + " ...")
    arcpy.Project_management(inFeature,prjInFeature,outputCoordinateSystem)
    deleteme.append(prjInFeature)
    
    if traversal < 360:
        
        initialBearing = bearing
        bearing = Geo2Arithmetic(bearing) # need to convert from geographic angles (zero north clockwise) to arithmetic (zero east counterclockwise)
        if traversal == 0: traversal = 1 # modify so there is at least 1 degree of angle.
        leftAngle = bearing - (traversal / 2.0)
        rightAngle = bearing + (traversal / 2.0)
        
        centerPoints = []
        arcpy.AddMessage("Getting centers ....")
        shapefieldname = arcpy.Describe(prjInFeature).ShapeFieldName
        rows = arcpy.SearchCursor(prjInFeature)
        for row in rows:
            feat = row.getValue(shapefieldname)
            pnt = feat.getPart()
            centerPointX = pnt.X
            centerPointY = pnt.Y
            centerPoints.append([centerPointX,centerPointY])
        del row
        del rows
        
        paths = []
        arcpy.AddMessage("Creating paths ...")
        for centerPoint in centerPoints:
            path = []
            centerPointX = centerPoint[0]
            centerPointY = centerPoint[1]
            path.append([centerPointX,centerPointY]) # add first point
            step = 1 # step in degrees
            #print "Left Angle, Right Angle" #UPDATE
            print("Left Angle, Right Angle")
            #print leftAngle,rightAngle #UPDATE
            print(leftAngle,rightAngle)
            #for d in xrange(int(leftAngle),int(rightAngle),step): #UPDATE
            for d in range(int(leftAngle),int(rightAngle),step):    
                x = centerPointX + (dRange * math.cos(math.radians(d)))
                y = centerPointY + (dRange * math.sin(math.radians(d)))
                path.append([x,y])
            path.append([centerPointX,centerPointY]) # add last point
            paths.append(path)
        
        arcpy.AddMessage("Creating target feature class ...")
        arcpy.CreateFeatureclass_management(os.path.dirname(outFeature),os.path.basename(outFeature),"Polygon","#","DISABLED","DISABLED",outputCoordinateSystem)
        arcpy.AddField_management(outFeature,"Range","DOUBLE")
        arcpy.AddField_management(outFeature,"Bearing","DOUBLE")
        
        arcpy.AddMessage("Building " + str(len(paths)) + " fans ...")
        cur = arcpy.InsertCursor(outFeature)
        for outPath in paths:
            lineArray = arcpy.Array()
            for vertex in outPath:
                pnt = arcpy.Point()
                pnt.X = vertex[0]
                pnt.Y = vertex[1]
                lineArray.add(pnt)
                del pnt
            feat = cur.newRow()
            feat.shape = lineArray
            feat.Range = dRange
            feat.Bearing = initialBearing
            cur.insertRow(feat)
            del lineArray
            del feat
        del cur
        
    else:
        if debug == True: arcpy.AddMessage("Traversal is 360 degrees, buffering instead ...")
        distance = str(dRange) + " Meters"
        arcpy.Buffer_analysis(prjInFeature,outFeature,distance)
    
    
    arcpy.SetParameter(4,outFeature)
    env.overwriteOutput = currentOverwriteOutput


except arcpy.ExecuteError: 
    # Get the tool error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    #print msgs #UPDATE
    print(msgs)

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
    #print pymsg + "\n" #UPDATE
    print(pymsg + "\n")
    #print msgs #UPDATE
    print(msgs)

finally:
    # cleanup intermediate datasets
    if debug == True: arcpy.AddMessage("Removing intermediate datasets...")
    for i in deleteme:
        arcpy.Delete_management(i)
        if debug == True: arcpy.AddMessage("Removing: " + str(i))
    if debug == True: arcpy.AddMessage("Done")
