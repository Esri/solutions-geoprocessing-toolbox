

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
inFeature = arcpy.GetParameterAsText(0)
rangeField = arcpy.GetParameterAsText(1)
bearingField = arcpy.GetParameterAsText(2) #45.0 # degrees
traversalField = arcpy.GetParameterAsText(3) #60.0 # degrees
outFeature = arcpy.GetParameterAsText(4)
webMercator = arcpy.GetParameterAsText(5)

deleteme = []
debug = False
leftAngle = 0.0 # degrees
rightAngle = 90.0 # degrees


try:

    if debug == True: arcpy.AddMessage("getting started ...")
    GCS_WGS_1984 = arcpy.SpatialReference("WGS 1984")
    #webMercator = os.path.join(installDirectory,r"Coordinate Systems", r"Projected Coordinate Systems",r"World",r"WGS 1984 Web Mercator (Auxiliary Sphere).prj")
    env.overwriteOutput = True
    scratch = env.scratchWorkspace
    
    prjInFeature = os.path.join(scratch,"prjInFeature")
    arcpy.AddMessage("Projecting input point to Web Mercator" + str(prjInFeature))
    arcpy.Project_management(inFeature,prjInFeature,webMercator)
    deleteme.append(prjInFeature)
    shapefieldname = arcpy.Describe(prjInFeature).ShapeFieldName
    
    arcpy.AddMessage("Creating out features ...")
    arcpy.CreateFeatureclass_management(os.path.dirname(outFeature),os.path.basename(outFeature),"Polygon","#","DISABLED","DISABLED",webMercator)
    arcpy.AddField_management(outFeature,"Range","DOUBLE")
    arcpy.AddField_management(outFeature,"Bearing","DOUBLE")
    
    rows = arcpy.SearchCursor(prjInFeature)
    cur = arcpy.InsertCursor(outFeature)
    for row in rows:
        feat = row.getValue(shapefieldname)
        pnt = feat.getPart()
        centerPointX = pnt.X
        centerPointY = pnt.Y
        range = row.getValue(rangeField)
        bearing = row.getValue(bearingField)
        traversal = row.getValue(traversalField)
        
        initialBearing = bearing
        bearing = Geo2Arithmetic(bearing)
        if traversal == 0: traversal = 1 # modify so there is at least 1 degree of angle.
        leftAngle = bearing - (traversal / 2.0)
        rightAngle = bearing + (traversal / 2.0)
    
        msg = "Constructing: " + str(centerPointX) + "," + str(centerPointY) + " from " + str(leftAngle) + " to " + str(rightAngle)
        arcpy.AddMessage(msg)
    
        path = []
        if traversal < 360: path.append([centerPointX,centerPointY]) 
        step = 1 # step in degrees
        #print "Left Angle, Right Angle"
        #print leftAngle,rightAngle
        for d in xrange(int(leftAngle),int(rightAngle),step):
            x = centerPointX + (range * math.cos(math.radians(d)))
            y = centerPointY + (range * math.sin(math.radians(d)))
            msg = str(d) + " @ " + str(range) + "m : " + str(x) + "," + str(y)
            if debug == True: arcpy.AddMessage(msg)
            path.append([x,y])
        if traversal < 360: path.append([centerPointX,centerPointY])
    
        lineArray = arcpy.Array()
    
        for vertex in path:
            pnt = arcpy.Point()
            pnt.X = vertex[0]
            pnt.Y = vertex[1]
            lineArray.add(pnt)
            del pnt
        feat = cur.newRow()
        feat.shape = lineArray
        feat.Range = range
        feat.Bearing = initialBearing
        if debug == True: arcpy.AddMessage("inserting feature into feature class")
        cur.insertRow(feat)
        del path
        del lineArray
        
    del cur
    del row
    del rows

    arcpy.SetParameter(4,outFeature)


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
