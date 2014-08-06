
# ==================================================
# AddUniqueRowID.py
# --------------------------------------------------
# Built for ArcGIS 10.1
# --------------------------------------------------
# Adds a new field of unique row numbers to a table
# ==================================================

# IMPORTS ==========================================
import os, sys, traceback
import arcpy
from arcpy import da

# ARGUMENTS ========================================
dataset = arcpy.GetParameterAsText(0)
fieldName = arcpy.GetParameterAsText(1)

# LOCALS ===========================================
counter = 1

# ==================================================
try:
    
    # add unique ID field
    arcpy.AddMessage("Adding field " + str(fieldName))
    arcpy.AddField_management(dataset,fieldName,"LONG")

    # add unique numbers to each row
    fields = [str(fieldName)]
    arcpy.AddMessage("Adding unique row IDs")
    rows = arcpy.da.UpdateCursor(dataset,fields)
    for row in rows:
        row[0] = counter
        rows.updateRow(row)
        counter += 1
    del rows
    
    # set output
    arcpy.SetParameter(0,dataset)
    

except arcpy.ExecuteError:
    error = True
    # Get the tool error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    #print msgs #UPDATE
    print(msgs)

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
    #print pymsg + "\n" #UPDATE
    print(pymsg + "\n")
    #print msgs #UPDATE
    print(msgs)