
# ==================================================
# ConvertCoordinates.py
# --------------------------------------------------
# Built for ArcGIS 10.1
# --------------------------------------------------
# Converts input coordinates to DD, DMS, DDM, UTM, MGRS, USNG, GARS, GeoRef
# ==================================================

# IMPORTS ==========================================
import sys, os, traceback
import arcpy
from arcpy import env

# ARGUMENTS ========================================
scriptpath = sys.path[0]
Input_Table = arcpy.GetParameterAsText(0)
Input_Coordinate_Format = arcpy.GetParameterAsText(1)
X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_ = arcpy.GetParameterAsText(2)
Y_Field__Latitude_ = arcpy.GetParameterAsText(3)
Output_Table = arcpy.GetParameterAsText(4)
Spatial_Reference = arcpy.GetParameterAsText(5)

# LOCALS ===========================================
delete_me = []

# ==================================================
try:
    # Load required toolboxes
    toolboxpath = os.path.join(scriptpath,"..\\Position Analysis Tools.tbx")
    arcpy.ImportToolbox(toolboxpath) #("C:\\Work\\TOS\\Intel\\Toolbox.tbx")

    # set environment
    currentOverwriteOutput = env.overwriteOutput
    env.overwriteOutput = True
    scratchWS = env.scratchWorkspace
    scratchTable = os.path.join(scratchWS,"cc_temp")
    delete_me.append(scratchTable)
    
    # Process: Copy Rows
    arcpy.CopyRows_management(Input_Table, Output_Table, "")
    
    # Process: Add Unique Row ID
    arcpy.gp.AddUniqueRowID(Output_Table, "JoinID")
    
    # Process: Convert Coordinate Notation (GARS)
    arcpy.AddMessage("Converting & appending GARS ...")
    arcpy.ConvertCoordinateNotation_management(Output_Table, scratchTable, X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_, Y_Field__Latitude_, Input_Coordinate_Format, "GARS", "JoinID", Spatial_Reference)
    arcpy.JoinField_management(Output_Table, "JoinID", scratchTable, "JoinID", "GARS")
    
    # Process: Convert Coordinate Notation (DD)
    arcpy.AddMessage("Converting & appending Decimal Degrees ...")
    arcpy.ConvertCoordinateNotation_management(Output_Table, scratchTable, X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_, Y_Field__Latitude_, Input_Coordinate_Format, "DD_2", "JoinID", Spatial_Reference)
    arcpy.JoinField_management(Output_Table, "JoinID", scratchTable, "JoinID", "DDLat;DDLon")
    
    # Process: Convert Coordinate Notation (DDM)
    arcpy.AddMessage("Converting & appending Degrees Decimal Minutes ...")
    arcpy.ConvertCoordinateNotation_management(Output_Table, scratchTable, X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_, Y_Field__Latitude_, Input_Coordinate_Format, "DDM_2", "JoinID", Spatial_Reference)
    arcpy.JoinField_management(Output_Table, "JoinID", scratchTable, "JoinID", "DDMLat;DDMLon")
    
    # Process: Convert Coordinate Notation (DMS)
    arcpy.AddMessage("Converting & appending Degrees Minutes Seconds ...")
    arcpy.ConvertCoordinateNotation_management(Output_Table, scratchTable, X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_, Y_Field__Latitude_, Input_Coordinate_Format, "DMS_2", "JoinID", Spatial_Reference)
    arcpy.JoinField_management(Output_Table, "JoinID", scratchTable, "JoinID", "DMSLat;DMSLon")
    
    # Process: Convert Coordinate Notation (UTM)
    arcpy.AddMessage("Converting & appending UTM ...")
    arcpy.ConvertCoordinateNotation_management(Output_Table, scratchTable, X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_, Y_Field__Latitude_, Input_Coordinate_Format, "UTM", "JoinID", Spatial_Reference)
    arcpy.JoinField_management(Output_Table, "JoinID", scratchTable, "JoinID", "UTM")
    
    # Process: Convert Coordinate Notation (MGRS)
    arcpy.AddMessage("Converting & appending MGRS ...")
    arcpy.ConvertCoordinateNotation_management(Output_Table, scratchTable, X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_, Y_Field__Latitude_, Input_Coordinate_Format, "MGRS", "JoinID", Spatial_Reference)
    arcpy.JoinField_management(Output_Table, "JoinID", scratchTable, "JoinID", "MGRS")
    
    # Process: Convert Coordinate Notation (USNG)
    arcpy.AddMessage("Converting & appending USNG ...")
    arcpy.ConvertCoordinateNotation_management(Output_Table, scratchTable, X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_, Y_Field__Latitude_, Input_Coordinate_Format, "USNG", "JoinID", Spatial_Reference)
    arcpy.JoinField_management(Output_Table, "JoinID", scratchTable, "JoinID", "USNG")
    
    # Process: Convert Coordinate Notation (GeoRef)
    arcpy.AddMessage("Converting & appending GeoRef ...")
    arcpy.ConvertCoordinateNotation_management(Output_Table, scratchTable, X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_, Y_Field__Latitude_, Input_Coordinate_Format, "GEOREF", "JoinID", Spatial_Reference)
    arcpy.JoinField_management(Output_Table, "JoinID", scratchTable, "JoinID", "GEOREF")
    
    # cleanup
    arcpy.AddMessage("Removing scratch datasets:")
    for ds in delete_me:
        arcpy.AddMessage(str(ds))
        if arcpy.Exists(ds):
            arcpy.Delete_management(ds)

    arcpy.SetParameter(0,Output_Table)
    
    
    
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
    print((pymsg + "\n"))
    #print msgs #UPDATE
    print(msgs)
