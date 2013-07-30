# 
# ==================================================
# AddTravelTimeToRoads.py
# --------------------------------------------------
# Built for ArcGIS 10.1
# ==================================================
# 
# Using the RoadTravelVelocity table this tool adds a
# travel cost in minutes to road features.
# 

# IMPORTS ==========================================
import os, sys, math, traceback
import arcpy
from arcpy import env
1000
# CONSTANTS ========================================

# FUNCTIONS ========================================
def CalcTravelTime(length,velocity):
    t = 0.0 # in minutes
    t = length * velocity
    return t

# ARGUMENTS & LOCALS ===============================
inputFeatures = arcpy.GetParameterAsText(0)
inputVelocityTable = arcpy.GetParameterAsText(1)
deleteme = []
debug = False

try:
    # Read table into dictionary {<TYP>:[<TF>,<FT>],...}
    velocityClasses = {}
    rows = arcpy.da.SearchCursor(inputVelocityTable,["typ","TF_KPH","FT_KPH"])
    for row in rows:
        velocityClasses[row[0]] = [row[1],row[2]]
    del rows
    
    # Add fields to inputFeatures
    fieldsToAdd = {"TF_MINUTES":"DOUBLE","FT_MINUTES":"DOUBLE"}
    fields = arcpy.ListFields(inputFeatures)
    fieldNames = []
    for f in fields: fieldNames.append(f.name)
    del fields
    if debug == True: arcpy.AddMessage(fieldNames)
    for addName in fieldsToAdd.iterkeys():
        fieldType = fieldsToAdd[addName]
        if not addName in fieldNames:
            arcpy.AddMessage("Adding " + addName + " field...")
            arcpy.AddField_management(inputFeatures,addName,fieldType)
        else:
            arcpy.AddWarning( addName + " exists. Updating existing field.")
   
    # TODO: go through roads, for each get roadclass and length. Calc time.....
    arcpy.AddMessage("Calculating travel time for " + str(int(arcpy.GetCount_management(inputFeatures).getOutput(0)) ) + " features ...")
    if debug == True: arcpy.AddMessage("OID, length, type, to-from, from-to")
    rows = arcpy.da.UpdateCursor(inputFeatures,["SHAPE@","TYP","TF_MINUTES","FT_MINUTES","OID@"])
    for row in rows:
        shape = row[0] # get shape for length property
        typ = row[1] # get road class type
        tf_velo = velocityClasses[typ][0] # use road type to look up velocities
        ft_velo = velocityClasses[typ][1]
        if not tf_velo == None:
            tf_velo = (tf_velo) * (1000.0/60.0) # convert kph to meters/minute
            tf_minutes = (shape.length / tf_velo) 
            row[2] = tf_minutes
        else:
            row[2] = None # if velocity is None, then time is None
        
        if not ft_velo == None:
            ft_velo = (ft_velo) * (1000.0/60.0)
            ft_minutes = (shape.length / ft_velo)
            row[3] = ft_minutes
        else:
            row[3] = None
        
        rows.updateRow(row)
        if debug == True: arcpy.AddMessage(str(row[4]) + ", " + str(shape.length) + ", " + str(row[1]) + ", " + str(row[2]) + ", " + str(row[3])) 
    del rows
    
    # Set output
    if debug == True: arcpy.AddMessage("Done.")
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
    if debug == False and len(deleteme) > 0:
        # cleanup intermediate datasets
        if debug == True: arcpy.AddMessage("Removing intermediate datasets...")
        for i in deleteme:
            if debug == True: arcpy.AddMessage("Removing: " + str(i))
            arcpy.Delete_management(i)
        if debug == True: arcpy.AddMessage("Done")