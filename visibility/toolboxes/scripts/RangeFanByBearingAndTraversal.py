
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

# ==================================================
# RangeFanByBearingAndTraversal.py
# --------------------------------------------------
# Built for ArcGIS Desktop 10.x and ArcGIS Pro 1.x
# ==================================================
# 2/5/2015 - mf - Updates to change Web Mercator to user-selected coordinate system


# IMPORTS ==========================================
import os, sys, math, traceback
import arcpy
from arcpy import env

# ARGUMENTS & LOCALS ===============================
inFeature = arcpy.GetParameterAsText(0)
weaponTable = arcpy.GetParameterAsText(1)
weaponField = arcpy.GetParameterAsText(2)
weaponModel = arcpy.GetParameterAsText(3)
maxRangeField = arcpy.GetParameterAsText(4)
maxRange = float(arcpy.GetParameterAsText(5)) #1000.0 # meters
geoBearing = float(arcpy.GetParameterAsText(6)) #45.0 # degrees
traversal = float(arcpy.GetParameterAsText(7)) #60.0 # degrees
outFeature = arcpy.GetParameterAsText(8)
commonSpatialReference = arcpy.GetParameter(9)
commonSpatialReferenceAsText = arcpy.GetParameterAsText(9)

deleteme = []
debug = False
leftAngle = 0.0 # degrees
rightAngle = 90.0 # degrees


# CONSTANTS ========================================


# FUNCTIONS ========================================
def Geo2Arithmetic(inAngle):
    outAngle = -1.0
    # force input angle into 0 to 360 range
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
        
    if debug == True: arcpy.AddMessage("G2A inAngle(" + str(inAngle) + "), outAngle(" + str(outAngle) + ")")
    return outAngle

try:

    currentOverwriteOutput = env.overwriteOutput
    env.overwriteOutput = True
        
    if commonSpatialReferenceAsText == '':
        commonSpatialReference = arcpy.Describe(inFeature).spatialReference
        arcpy.AddWarning("Spatial Reference is not defined. Using Spatial Reference of input features: " + str(commonSpatialReference.name))    
    env.outputCoordinateSystem = commonSpatialReference
    
    env.overwriteOutput = True
    scratch = env.scratchWorkspace
    
    #Project doesn't like in_memory featureclasses, copy to scratch
    copyInFeatures = os.path.join(scratch,"copyInFeatures")
    arcpy.CopyFeatures_management(inFeature,copyInFeatures)
    deleteme.append(copyInFeatures)
    
    prjInFeature = os.path.join(scratch,"prjInFeature")
    srInputPoints = arcpy.Describe(copyInFeatures).spatialReference
    arcpy.AddMessage("Projecting input points to " + str(env.outputCoordinateSystem.name) + " ...")
    arcpy.Project_management(copyInFeatures,prjInFeature,env.outputCoordinateSystem)
    deleteme.append(prjInFeature)
    tempFans = os.path.join(scratch,"tempFans")
            
    # put bearing into 0 - 360 range
    geoBearing = math.fmod(geoBearing,360.0)
    if debug == True: arcpy.AddMessage("geoBearing: " + str(geoBearing))
    arithmeticBearing = Geo2Arithmetic(geoBearing) # need to convert from geographic angles (zero north clockwise) to arithmetic (zero east counterclockwise)
    if debug == True: arcpy.AddMessage("arithmeticBearing: " + str(arithmeticBearing))
    
    if traversal == 0.0:
        traversal = 1.0 # modify so there is at least 1 degree of angle.
        arcpy.AddWarning("Traversal is zero! Forcing traversal to 1.0 degrees.")
    leftAngle = arithmeticBearing + (traversal / 2.0) # get left angle (arithmetic)
    leftBearing = geoBearing - (traversal / 2.0) # get left bearing (geographic)
    if leftBearing < 0.0: leftBearing = 360.0 + leftBearing
    
    rightAngle = arithmeticBearing - (traversal / 2.0) # get right angle (arithmetic)
    rightBearing = geoBearing + (traversal / 2.0) # get right bearing (geographic)
    if rightBearing < 0.0: rightBearing = 360.0 + rightBearing
    
    if debug == True: arcpy.AddMessage("arithemtic left/right: " + str(leftAngle) + "/" + str(rightAngle))
    if debug == True: arcpy.AddMessage("geo left/right: " + str(leftBearing) + "/" + str(rightBearing))
    
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
        step = -1.0 # step in degrees
        rightAngleRelativeToLeft = leftAngle - traversal - 1
        #for d in xrange(int(leftAngle),int(rightAngleRelativeToLeft),int(step)): #UPDATE
        for d in range(int(leftAngle),int(rightAngleRelativeToLeft),int(step)):
            x = centerPointX + (maxRange * math.cos(math.radians(d)))
            y = centerPointY + (maxRange * math.sin(math.radians(d)))
            path.append([x,y])
            if debug == True: arcpy.AddMessage("d,x,y: " + str(d) + "," + str(x) + "," + str(y))    
        path.append([centerPointX,centerPointY]) # add last point
        paths.append(path)
        if debug == True: arcpy.AddMessage("Points in path: " + str(len(path)))
    if debug == True: arcpy.AddMessage("paths: " + str(paths))
    
    arcpy.AddMessage("Creating target feature class ...")
    arcpy.CreateFeatureclass_management(os.path.dirname(tempFans),os.path.basename(tempFans),"Polygon","#","DISABLED","DISABLED",env.outputCoordinateSystem)
    arcpy.AddField_management(tempFans,"Range","DOUBLE","#","#","#","Range (meters)")
    arcpy.AddField_management(tempFans,"Bearing","DOUBLE","#","#","#","Bearing (degrees)")
    arcpy.AddField_management(tempFans,"Traversal","DOUBLE","#","#","#","Traversal (degrees)")
    arcpy.AddField_management(tempFans,"LeftAz","DOUBLE","#","#","#","Left Bearing (degrees)")
    arcpy.AddField_management(tempFans,"RightAz","DOUBLE","#","#","#","Right Bearing (degrees)")
    arcpy.AddField_management(tempFans,"Model","TEXT","#","#","#","Weapon Model")
    deleteme.append(tempFans)
    
    arcpy.AddMessage("Building " + str(len(paths)) + " fans ...")
    cur = arcpy.InsertCursor(tempFans)
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
        feat.Range = maxRange
        feat.Bearing = geoBearing
        feat.Traversal = traversal
        feat.LeftAz = leftBearing
        feat.RightAz = rightBearing
        feat.Model = str(weaponModel)
        cur.insertRow(feat)
        del lineArray
        del feat
    del cur
            
    arcpy.AddMessage("Projecting Range Fans back to " + str(srInputPoints.name))
    arcpy.Project_management(tempFans,outFeature,srInputPoints)
    
    arcpy.SetParameter(8,outFeature)
    

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
    msgs = "\nArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

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
        if debug == True: arcpy.AddMessage("Removing: " + str(i))
        arcpy.Delete_management(i)
    if debug == True: arcpy.AddMessage("Done")
