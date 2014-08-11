
# ==================================================
# RangeFanByBearingLimits.py
# --------------------------------------------------
# Built for ArcGIS 10.1
# ==================================================


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
leftBearing = float(arcpy.GetParameterAsText(6)) #75.0 # degrees
rightBearing = float(arcpy.GetParameterAsText(7)) #270.0 # degrees
outFeature = arcpy.GetParameterAsText(8)

deleteme = []
debug = True
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

    return outAngle

try:

    # set some intial stuff
    if debug == True: arcpy.AddMessage("START ....")
    currentOverwriteOutput = env.overwriteOutput
    env.overwriteOutput = True
    sr = arcpy.SpatialReference()
    sr.factoryCode = 4326
    sr.create()
    GCS_WGS_1984 = sr
    #GCS_WGS_1984 = arcpy.SpatialReference(r"WGS 1984")
    wbsr = arcpy.SpatialReference()
    wbsr.factoryCode = 3857
    wbsr.create()
    webMercator = wbsr
    #webMercator = arcpy.SpatialReference(r"WGS 1984 Web Mercator (Auxiliary Sphere)")    
    env.overwriteOutput = True
    scratch = env.scratchWorkspace
    #scratch = r"C:\Users\matt2542\Documents\ArcGIS\Default.gdb"
    
    #Project doesn't like in_memory featureclasses, copy to scratch
    if debug == True: arcpy.AddMessage("CopyFeatures ....")
    copyInFeatures = os.path.join(scratch,"copyInFeatures")
    arcpy.CopyFeatures_management(inFeature,copyInFeatures)
    deleteme.append(copyInFeatures)
    
    # project inputs to Web Mercator so we're working with meters
    prjInFeature = os.path.join(scratch,"prjInFeature")
    srInputPoints = arcpy.Describe(copyInFeatures).spatialReference
    arcpy.AddMessage("Projecting input points to Web Mercator ...")
    arcpy.Project_management(copyInFeatures,prjInFeature,webMercator)
    deleteme.append(prjInFeature)
    tempFans = os.path.join(scratch,"tempFans")

    initialBearing = -9999.0
    traversal = -9999.0
    # get mod of 360.0
    leftBearing = math.fmod(leftBearing,360.0)
    rightBearing = math.fmod(rightBearing, 360.0)
    
    # calc traversal and center (initial) bearing from limits
    if (leftBearing == rightBearing):
        arcpy.AddWarning("Left and Right Bearings are equal! Applying 1 degree offset to Right Bearing.")
        rightBearing += 1
    
    if (leftBearing < rightBearing):
        traversal = rightBearing - leftBearing
        initialBearing = math.fmod(leftBearing + (traversal/2.0),360.0)
        
    else:
        # if left bearing > right bearing: ex L:180, R:90, eg. traversal is 270deg with initial bearing at 315 deg
        traversal = (360.0 - leftBearing) + rightBearing
        initialBearing = math.fmod(leftBearing + (traversal/2.0),360.0)
    
    # change Angles from geogaphic to arithmetic for geometry calc
    initialAngle = Geo2Arithmetic(initialBearing)
    leftAngle = Geo2Arithmetic(leftBearing)
    rightAngle = Geo2Arithmetic(rightBearing)
    
    if debug == True:
        msg = "leftBearing: " + str(leftBearing) + ", leftAngle: " + str(leftAngle)
        msg += "\nrightBearing: " + str(rightBearing) + ", rightAngle: " + str(rightAngle)
        msg += "\ntraversal: " + str(traversal) + ", initalBearing: " + str(initialBearing)
        arcpy.AddMessage(msg)
    
    # get a list of range fan center points
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
    del rows
    if debug == True: arcpy.AddMessage("centerPoints: " + str(centerPoints))
    
    # for each center, create the points for the range fan
    paths = []
    arcpy.AddMessage("Creating paths ...")
    for centerPoint in centerPoints:
        path = []
        centerPointX = centerPoint[0]
        centerPointY = centerPoint[1]
        path.append([centerPointX,centerPointY]) # add first point
        
        step = -1.0 # step in degrees
        rightAngleRelativeToLeft = leftAngle - traversal - 1
        for d in xrange(int(leftAngle),int(rightAngleRelativeToLeft),int(step)):
            x = centerPointX + (maxRange * math.cos(math.radians(d)))
            y = centerPointY + (maxRange * math.sin(math.radians(d)))
            path.append([x,y])
            if debug == True: arcpy.AddMessage("d,x,y: " + str(d) + "," + str(x) + "," + str(y))    
        path.append([centerPointX,centerPointY]) # add last point
        paths.append(path)
        if debug == True: arcpy.AddMessage("Points in path: " + str(len(path)))
    if debug == True: arcpy.AddMessage("paths: " + str(paths))
    
    arcpy.AddMessage("Creating target feature class ...")
    arcpy.CreateFeatureclass_management(os.path.dirname(tempFans),os.path.basename(tempFans),"Polygon","#","DISABLED","DISABLED",webMercator)
    arcpy.AddField_management(tempFans,"Range","DOUBLE","#","#","#","Range (meters)")
    arcpy.AddField_management(tempFans,"Bearing","DOUBLE","#","#","#","Bearing (degrees)")
    arcpy.AddField_management(tempFans,"Traversal","DOUBLE","#","#","#","Traversal (degrees)")
    arcpy.AddField_management(tempFans,"LeftAz","DOUBLE","#","#","#","Left Bearing (degrees)")
    arcpy.AddField_management(tempFans,"RightAz","DOUBLE","#","#","#","Right Bearing (degrees)")
    arcpy.AddField_management(tempFans,"Model","TEXT","#","#","#","Weapon Model")
    deleteme.append(tempFans)
    
    # take the points and add them into the output fc
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
        feat.Bearing = initialBearing
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
