
# for line features, finds the bearing angle from the first point to the last point

import os, sys, traceback, math
import arcpy

def Geo2Arithmetic(inAngle):
    inAngle = math.fmod(inAngle,360.0)
    #0 to 90
    if (inAngle >= 0.0 and inAngle <= 90.0):
        outAngle = math.fabs(inAngle - 90.0)
    # 90 to 360
    if (inAngle >= 90.0 and inAngle < 360.0):
        outAngle = 360.0 - (inAngle - 90.0)
    return float(outAngle)


inputFeatures = arcpy.GetParameterAsText(0) # C:\Workspace\ArcGIS Defense 10.1\path slope\default.gdb\roads
inputAngleField = arcpy.GetParameterAsText(1) # aoo
deleteme = []
debug = False

try:

    arcpy.AddMessage("Updating " + inputAngleField + " field for " + str(arcpy.GetCount_management(inputFeatures).getOutput(0)) + " rows ...")
    with arcpy.da.UpdateCursor(inputFeatures,["OID@","SHAPE@",inputAngleField]) as rows:
        for row in rows:
            angle = None
            geometry = row[1] # firstPoint, lastPoint
            firstPoint = geometry.firstPoint
            lastPoint = geometry.lastPoint
            xdiff = (lastPoint.X - firstPoint.X)
            ydiff = (lastPoint.Y - firstPoint.Y)
            #distance = math.sqrt(math.pow(xdiff,2.0) + math.pow(ydiff,2.0))
            
            # Convert from quadrants to arithmetic
            if (xdiff == 0.0 and ydiff > 0.0):
                # vertical line, slope infinity
                angle = 90.0
            if (xdiff == 0.0 and ydiff < 0.0):
                # vertical line, slope infinity
                angle = 270.0
            if (xdiff > 0.0 and ydiff == 0.0):
                angle = 0.0
            if (xdiff < 0.0 and ydiff == 0.0):
                angle = 180.0
            if (xdiff > 0.0 and ydiff > 0.0): # Quadrant I (+,+)
                angle = math.degrees(math.atan(ydiff/xdiff))
            if (xdiff < 0.0 and ydiff > 0.0): # Quadrant II (-,+)
                angle = 180.0 - math.fabs(math.degrees(math.atan(ydiff/xdiff)))
            if (xdiff < 0.0 and ydiff < 0.0): # Quadrant III (-,-)
                angle = 180.0 + math.fabs(math.degrees(math.atan(ydiff/xdiff)))
            if (xdiff > 0.0 and ydiff < 0.0): # Quadrant IV (+,-)
                angle = 360.0 - math.fabs(math.degrees(math.atan(ydiff/xdiff)))
            
            #if debug == True: arcpy.AddMessage(str(xdiff) + " -- " + str(angle) + " -- " + str(ydiff))
            
            if not angle == None:
                row[2] = Geo2Arithmetic(angle)
            else:
                arcpy.AddWarning("Empty angle for feature " + str(row[0]) + ". This could be a closed loop feature.")
                row[2] = None
            #if debug == True: arcpy.AddMessage("   " + str(row))
            rows.updateRow(row)

    arcpy.SetParameter(2,inputFeatures)

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