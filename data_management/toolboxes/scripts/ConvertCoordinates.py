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
# Name: ConvertCoordinates.py
# Description: ConvertCoordinates
# Requirements: ArcGIS Desktop Standard
#------------------------------------------------------------------------------

#Imports
import sys, os, traceback
import arcpy
from arcpy import env

delete_me = []

try:
    
    # Load required toolboxes
    scriptpath = sys.path[0]
    #toolboxpath = os.path.join(scriptpath,"..\\Position Analysis Tools.tbx")
    toolboxpath = os.path.join(scriptpath,"..\\Import and Conversion Tools_10.3.tbx")
    arcpy.ImportToolbox(toolboxpath) 
    
    # Script arguments
    Input_Table = arcpy.GetParameterAsText(0)
    arcpy.AddMessage(Input_Table)
    if Input_Table == '#' or not Input_Table:
        Input_Table = "C:\\Workspace\\Data\\Geometry Importers\\linewizard.dbf" # provide a default value if unspecified
    
    Input_Coordinate_Format = arcpy.GetParameterAsText(1)
    if Input_Coordinate_Format == '#' or not Input_Coordinate_Format:
        Input_Coordinate_Format = "DD" # provide a default value if unspecified
    
    X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_ = arcpy.GetParameterAsText(2)
    if X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_ == '#' or not X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_:
        X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_ = "Lond" # provide a default value if unspecified
    
    Y_Field__Latitude_ = arcpy.GetParameterAsText(3)
    if Y_Field__Latitude_ == '#' or not Y_Field__Latitude_:
        Y_Field__Latitude_ = "Latd" # provide a default value if unspecified
    
    Output_Table = arcpy.GetParameterAsText(4)
    arcpy.AddMessage(Output_Table)
    if Output_Table == '#' or not Output_Table:
        pass
    
    Spatial_Reference = arcpy.GetParameterAsText(5)
    if Spatial_Reference == '#' or not Spatial_Reference:
        Spatial_Reference = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119522E-09;0.001;0.001;IsHighPrecision" # provide a default value if unspecified
    
    currentOverwriteOutput = env.overwriteOutput
    env.overwriteOutput = True
    
    scratchWS = env.scratchWorkspace
    if scratchWS == None:
        scratchWS = r'in_memory'

    
    scratchTable = os.path.join(scratchWS,"cc_temp")
    delete_me.append(scratchTable)
    
    # Local variables:
    intermed = Output_Table
    
    # Process: Copy Rows
    arcpy.CopyRows_management(Input_Table, Output_Table, "")
    
    # Process: Add Unique Row ID
    arcpy.AddUniqueRowID_InC(Output_Table, "JoinID")
    
    # Process: Convert Coordinate Notation (GARS)
    arcpy.AddMessage("Converting & appending GARS ...")
    arcpy.ConvertCoordinateNotation_management(intermed, scratchTable, X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_, Y_Field__Latitude_, Input_Coordinate_Format, "GARS", "JoinID", Spatial_Reference)
    arcpy.JoinField_management(intermed, "JoinID", scratchTable, "JoinID", "GARS")
    
    # Process: Convert Coordinate Notation (DD)
    arcpy.AddMessage("Converting & appending Decimal Degrees ...")
    arcpy.ConvertCoordinateNotation_management(intermed, scratchTable, X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_, Y_Field__Latitude_, Input_Coordinate_Format, "DD", "JoinID", Spatial_Reference)
    arcpy.JoinField_management(intermed, "JoinID", scratchTable, "JoinID", "DDLat;DDLon")
    
    # Process: Convert Coordinate Notation (DDM)
    arcpy.AddMessage("Converting & appending Degrees Decimal Minutes ...")
    arcpy.ConvertCoordinateNotation_management(intermed, scratchTable, X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_, Y_Field__Latitude_, Input_Coordinate_Format, "DDM", "JoinID", Spatial_Reference)
    arcpy.JoinField_management(intermed, "JoinID", scratchTable, "JoinID", "DDMLat;DDMLon")
    
    # Process: Convert Coordinate Notation (DMS)
    arcpy.AddMessage("Converting & appending Degrees Minutes Seconds ...")
    arcpy.ConvertCoordinateNotation_management(intermed, scratchTable, X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_, Y_Field__Latitude_, Input_Coordinate_Format, "DMS", "JoinID", Spatial_Reference)
    arcpy.JoinField_management(intermed, "JoinID", scratchTable, "JoinID", "DMS")
    
    # Process: Convert Coordinate Notation (UTM)
    arcpy.AddMessage("Converting & appending UTM ...")
    arcpy.ConvertCoordinateNotation_management(intermed, scratchTable, X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_, Y_Field__Latitude_, Input_Coordinate_Format, "UTM", "JoinID", Spatial_Reference)
    arcpy.JoinField_management(intermed, "JoinID", scratchTable, "JoinID", "UTM")
    
    # Process: Convert Coordinate Notation (MGRS)
    arcpy.AddMessage("Converting & appending MGRS ...")
    arcpy.ConvertCoordinateNotation_management(intermed, scratchTable, X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_, Y_Field__Latitude_, Input_Coordinate_Format, "MGRS", "JoinID", Spatial_Reference)
    arcpy.JoinField_management(intermed, "JoinID", scratchTable, "JoinID", "MGRS")
    
    # Process: Convert Coordinate Notation (USNG)
    arcpy.AddMessage("Converting & appending USNG ...")
    arcpy.ConvertCoordinateNotation_management(intermed, scratchTable, X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_, Y_Field__Latitude_, Input_Coordinate_Format, "USNG", "JoinID", Spatial_Reference)
    arcpy.JoinField_management(intermed, "JoinID", scratchTable, "JoinID", "USNG")
    
    # Process: Convert Coordinate Notation (GeoRef)
    arcpy.AddMessage("Converting & appending GeoRef ...")
    arcpy.ConvertCoordinateNotation_management(intermed, scratchTable, X_Field__Longitude__UTM__MGRS__USNG__GARS__GeoRef_, Y_Field__Latitude_, Input_Coordinate_Format, "GEOREF", "JoinID", Spatial_Reference)
    arcpy.JoinField_management(intermed, "JoinID", scratchTable, "JoinID", "GEOREF")
    
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
