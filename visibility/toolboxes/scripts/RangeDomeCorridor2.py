
# Esri start of added imports
import sys, os, arcpy
# Esri end of added imports

# Esri start of added variables
g_ESRI_variable_1 = '256'
g_ESRI_variable_2 = 'NONE'
g_ESRI_variable_3 = 'OBJECTID'
g_ESRI_variable_4 = '*.png'
g_ESRI_variable_5 = 'RELATIVE'
g_ESRI_variable_6 = 'MatchID'
g_ESRI_variable_7 = 'Filename'
g_ESRI_variable_8 = 'FREQUENCY'
g_ESRI_variable_9 = 'ZERO'
g_ESRI_variable_10 = '1'
g_ESRI_variable_11 = 'FLAT_EARTH'
g_ESRI_variable_12 = '0.13'
g_ESRI_variable_13 = 'Range'
g_ESRI_variable_14 = 'LeftAz'
g_ESRI_variable_15 = 'RightAz'
g_ESRI_variable_16 = 'FULL'
g_ESRI_variable_17 = 'FLAT'
g_ESRI_variable_18 = 'LIST'
g_ESRI_variable_19 = 'PLANAR'
g_ESRI_variable_20 = 'Full'
g_ESRI_variable_21 = 'ROUND'
g_ESRI_variable_22 = 'POINT_REMOVE'
g_ESRI_variable_23 = '100 Meters'
g_ESRI_variable_24 = '0 SquareMeters'
g_ESRI_variable_25 = 'NO_CHECK'
g_ESRI_variable_26 = 'KEEP_COLLAPSED_POINTS'
g_ESRI_variable_27 = 'BILINEAR'
g_ESRI_variable_28 = 'DENSIFY'
g_ESRI_variable_29 = '0'
g_ESRI_variable_30 = 'STRAIGHT'
g_ESRI_variable_31 = '15'
g_ESRI_variable_32 = 'SOLID'
g_ESRI_variable_33 = 'RangeLethal'
g_ESRI_variable_34 = '100'
g_ESRI_variable_35 = '1500000'
g_ESRI_variable_36 = '1024'
g_ESRI_variable_37 = 'Area'
g_ESRI_variable_38 = 'SArea'
g_ESRI_variable_39 = '2'
# Esri end of added variables

# -*- #################
# ---------------------------------------------------------------------------
# RangeDomeCorridor.py
# Created on: 2015-08-28
# Usage: RangeDomeCorridor <Threat_Positions> <Air_Corridor> <Distance> <Elevation> <Flight_Corridor_Dangerous> <Flight_Corridor_Lethal> <FlightCorridor_Dangerous_error> <FlightCorridor_Lethal_error>
# Description:
# Run threat domes analysis
# ---------------------------------------------------------------------------

# Set the necessary product code
import arceditor


# Import arcpy module and OS module
import arcpy
import arceditor
import os

# Enable Overwrite of Outputs
arcpy.env.overwriteOutput=True

# Check out any necessary licenses
arcpy.CheckOutExtension("3D")

#Find location of project-specific items
aprx = arcpy.mp.ArcGISProject("CURRENT")
HomePath = aprx.homeFolder
ToolboxPath = os.path.join(HomePath, "RangeDomePyProTools.pyt")
RequiredData = os.path.join(HomePath, "data")
#ShapefilePath = os.path.join(RequiredData, "CorridorBuffer.shp")


# Load required toolboxes
arcpy.ImportToolbox(ToolboxPath)

# Script arguments
Threat_Positions = arcpy.GetParameterAsText(0)
Air_Corridor = arcpy.GetParameterAsText(1)
Distance = arcpy.GetParameterAsText(2)
if Distance == '#' or not Distance:
    Distance = "250 Meters" # provide a default value if unspecified
Elevation = arcpy.GetParameterAsText(3)
Flight_Corridor_Dangerous = arcpy.GetParameterAsText(4)
Flight_Corridor_Lethal = arcpy.GetParameterAsText(5)
FlightCorridor_Dangerous_error = arcpy.GetParameterAsText(6)
FlightCorridor_Lethal_error = arcpy.GetParameterAsText(7)
#Intermediate Location work-aound for problems with scratch GDB on packaging Project Template
#Remove this parameter from tool if resolved
IntermediateLocation = arcpy.GetParameterAsText(8)
WorkingFolder = arcpy.env.scratchFolder

# Set Intermediate GDB Folder
out_folder_path = IntermediateLocation
out_name = "intermediate.gdb"

# Execute CreateFileGDB
intermediateGDB = arcpy.CreateFileGDB_management(out_folder_path, out_name)
outGDB = os.path.join(out_folder_path, out_name)

#Local variables:
Weapon_Positions_3D = os.path.join(outGDB, "WeaponPositions3D")
Lethal_3D_Buffer_Zone = os.path.join(outGDB, "buffinner")
Corridor_Lethal = os.path.join(outGDB, "QA_MinZone")
QA_MinZone_CE_enclosed_Featu = os.path.join(outGDB, "QA_MinZone_CE_enclosed_Featu")
QA_MinZone_CE_enclosed_Featu_MPoints = os.path.join(outGDB, "QA_MinZone_CE_enclosed_Featu_MPoints")
Max_3D_Buffer_Zone = os.path.join(outGDB, "buffouter")
Corridor_Max = os.path.join(outGDB, "QA_MaxZone")
QA_MaxZone_FeaturesFromCityE = os.path.join(outGDB, "QA_MaxZone_FeaturesFromCityE")
Visibility_Raster__Yes_No_ = os.path.join(outGDB, "rgd_viz2")
Visibility_Raster__RTG_Height_ = os.path.join(outGDB, "rgd_visrtg")
Visibility_Raster__ABS_Height_ = os.path.join(outGDB, "grd_VisABS")
Visibility_TIN__ABS_Height_ = os.path.join(arcpy.env.scratchGDB, "grd_VisABS_RasterTin2")
Ground_Zone__Mesh_ = os.path.join(outGDB, "grd_VisABS_MP")
DomePlusGround = os.path.join(outGDB, "DomePlusGround")
v2D_Zone = os.path.join(outGDB, "v2D_Zone")
v2D_Zone__SinglePart_ = os.path.join(outGDB, "d2ZoneSng")
v2D_Zone__Simplified_ = os.path.join(outGDB, "d2zonesmp")
QA_MaxZone_FeaturesFromCityE = os.path.join(outGDB, "QA_MaxZone_FeaturesFromCityE")
Corridor_Buffer = os.path.join(outGDB, "CorridorBufferMPart")
#CorridorBuffer_shp = ShapefilePath
CorridorBuffer_shp =  os.path.join(outGDB, "CorridorBuffer")

# Setting RPK variables to RPK files in commondata folder
cleanUpGeometry_rpk = os.path.join(HomePath, "RPK/cleanUpGeometry.rpk")
Extrude_WorldY_RangeAttr_rpk = os.path.join(HomePath, "RPK/Extrude_WorldY_RangeAttr.rpk")
Extrude_WorldY_Zmax_rpk = os.path.join(HomePath, "RPK/Extrude_WorldY_Zmax.rpk")

# Setting Warning Lethal and Warning Dangerous image paths to common data folder
WarningDangerous_png = os.path.join(RequiredData, "WarningDangerous.png")
WarningLethal_png = os.path.join(RequiredData, "WarningLethal.png")

CorridorVolume = "CorridorVolume"
DomePlusGround = "DomePlusGround"
QA_MaxZone_CE_enclosed = "QA_MaxZone_CE_enclosed"
QA_MinZone_CE_enclosed = "QA_MinZone_CE_enclosed"

# Function to make and append images to error features
def make_append_warning_images(in_error_features, in_error_image):
    tempMatchTable = "tempMatchTable"
    scratch_folder = arcpy.env.scratchFolder
    # make temp_images folder if it does not exist
    if not os.path.exists(os.path.join(scratch_folder, "temp_images")):
        os.makedirs(os.path.join(scratch_folder, "temp_images"))
        tempFolder = (os.path.join(scratch_folder, "temp_images"))

    # iterate error features, get OID numbers, make copies of the appropriate warning image
    tempFolder = (os.path.join(scratch_folder, "temp_images"))
    with arcpy.da.SearchCursor(in_error_features, ['OID@']) as cursor:
        for row in cursor:
            imageOutput = os.path.join(tempFolder, str(row[0])+".png")
            arcpy.CopyRaster_management(in_error_image, imageOutput, "", "", g_ESRI_variable_1, g_ESRI_variable_2, g_ESRI_variable_2, "", g_ESRI_variable_2, g_ESRI_variable_2)
    del cursor


    # Process: Enable Attachments
    arcpy.EnableAttachments_management(in_error_features)
    arcpy.AddMessage("Attachments enabled on " + str(in_error_features))

    # Process: Generate Attachment Match Table
    arcpy.GenerateAttachmentMatchTable_management(in_error_features, tempFolder, tempMatchTable, g_ESRI_variable_3, g_ESRI_variable_4, g_ESRI_variable_5)
    arcpy.AddMessage("Attachment Match Table generated.")
    # Process: Add Attachments
    arcpy.AddAttachments_management(in_error_features, g_ESRI_variable_3, tempMatchTable, g_ESRI_variable_6, g_ESRI_variable_7, tempFolder)

    filelist = [ f for f in os.listdir(tempFolder) ]
    for a_file in filelist:
        del_file_path_name = os.path.join(tempFolder, a_file)
        if os.path.isfile(del_file_path_name):
            os.remove(del_file_path_name)
    arcpy.AddMessage("Attachments added to " + str(in_error_features) + ".")
    arcpy.Delete_management(tempMatchTable)


# Process: Visibility
arcpy.AddMessage("Calculating visibility from threat positions.")
arcpy.Visibility_3d(Elevation, Threat_Positions, Visibility_Raster__Yes_No_, Visibility_Raster__RTG_Height_, g_ESRI_variable_8, g_ESRI_variable_9, g_ESRI_variable_10, g_ESRI_variable_11, g_ESRI_variable_12, "", "", "", "", g_ESRI_variable_13, g_ESRI_variable_14, g_ESRI_variable_15, "", "")

# Process: Buffer
arcpy.AddMessage("Buffering air corridor by " + str(Distance)+ ".")
arcpy.Buffer_analysis(Air_Corridor, Corridor_Buffer, Distance, g_ESRI_variable_16, g_ESRI_variable_17, g_ESRI_variable_18, ["ZMin","ZMax"], g_ESRI_variable_19)

# Process: Multipart To Singlepart
arcpy.AddMessage("Converting corridor buffer to single part features.")
arcpy.MultipartToSinglepart_management(Corridor_Buffer, CorridorBuffer_shp)

# Process: Buffer (2D)
arcpy.AddMessage("Buffering threat positions by range values.")
arcpy.Buffer_analysis(Threat_Positions, v2D_Zone, g_ESRI_variable_13, g_ESRI_variable_20, g_ESRI_variable_21, g_ESRI_variable_2, "", g_ESRI_variable_19)

# Process: Multipart To Singlepart
arcpy.AddMessage("Converting threat positions buffer to single part features.")
arcpy.MultipartToSinglepart_management(v2D_Zone, v2D_Zone__SinglePart_)

# Process: Simplify Polygon
arcpy.AddMessage("Simplifying threat position buffers.")
arcpy.SimplifyPolygon_cartography(v2D_Zone__SinglePart_, v2D_Zone__Simplified_, g_ESRI_variable_22, g_ESRI_variable_23, g_ESRI_variable_24, g_ESRI_variable_25, g_ESRI_variable_26)

# Process: Interpolate Shape
arcpy.AddMessage("Interpolating 3D features for weapons positions.")
arcpy.InterpolateShape_3d(Elevation, Threat_Positions, Weapon_Positions_3D, "", g_ESRI_variable_10, g_ESRI_variable_27, g_ESRI_variable_28, g_ESRI_variable_29)

# Process: Buffer 3D Max Range Zone
arcpy.AddMessage("Creating 3D volume features around weapons positions at maximum range.")
arcpy.Buffer3D_3d(Weapon_Positions_3D, Max_3D_Buffer_Zone, g_ESRI_variable_13, g_ESRI_variable_30, g_ESRI_variable_31, "")

# Process: Features From CityEngine Rules (4)
arcpy.AddMessage("Applying CityEngine Rules to Air Corridor buffers to make corridor volumes.")
arcpy.FeaturesFromCityEngineRules_3d(CorridorBuffer_shp, Extrude_WorldY_Zmax_rpk, CorridorVolume)

# Process: Int3D Max Sphere Corridor
arcpy.AddMessage("Intersecting maximum range threat position volumes and corridor buffer volumes.")
arcpy.Intersect3D_3d(Max_3D_Buffer_Zone, Corridor_Max, CorridorVolume, g_ESRI_variable_32)

# Process: Features From CityEngine Rules (3)
arcpy.AddMessage("Applying CityEngine rules to clean up air corridor volumes.")
arcpy.FeaturesFromCityEngineRules_3d(Corridor_Max, cleanUpGeometry_rpk, QA_MaxZone_FeaturesFromCityE)

# Process: Buffer 3D Lethal Zone
arcpy.AddMessage("Creating 3D volume features around weapons positions at lethal range.")
arcpy.Buffer3D_3d(Weapon_Positions_3D, Lethal_3D_Buffer_Zone, g_ESRI_variable_33, g_ESRI_variable_30, g_ESRI_variable_31, "")

# Process: Int3D Min Sphere Corridor
arcpy.AddMessage("Intersecting lethal range threat position volumes and corridor buffer volumes.")
arcpy.Intersect3D_3d(Lethal_3D_Buffer_Zone, Corridor_Lethal, CorridorVolume, g_ESRI_variable_32)

# Process: Features From CityEngine Rules (2)
arcpy.AddMessage("Applying CityEngine rules to clean up lethal corridor volumes.")
arcpy.FeaturesFromCityEngineRules_3d(Corridor_Lethal, cleanUpGeometry_rpk, QA_MinZone_CE_enclosed_Featu)

# Process: Plus
arcpy.AddMessage("Calculating absolute heights visible from threat positions.")
arcpy.Plus_3d(Elevation, Visibility_Raster__RTG_Height_, Visibility_Raster__ABS_Height_)

# Process: Raster to TIN
arcpy.AddMessage("Converting absolute height raster to TIN.")
arcpy.RasterTin_3d(Visibility_Raster__ABS_Height_, Visibility_TIN__ABS_Height_, g_ESRI_variable_34, g_ESRI_variable_35, g_ESRI_variable_10)

# Process: Interpolate Polygon to Multipatch
arcpy.AddMessage("Interpolating surface for base of threat volume features.")
arcpy.InterpolatePolyToPatch_3d(Visibility_TIN__ABS_Height_, v2D_Zone__Simplified_, Ground_Zone__Mesh_, g_ESRI_variable_36, g_ESRI_variable_10, g_ESRI_variable_37, g_ESRI_variable_38, g_ESRI_variable_29)

# Process: Features From CityEngine Rules
arcpy.AddMessage("Applying CityEngine rules to create dome segments with bases at threat volume absolute height.")
arcpy.FeaturesFromCityEngineRules_3d(Ground_Zone__Mesh_, Extrude_WorldY_RangeAttr_rpk, DomePlusGround)

# Process: Enclose Multipatch
arcpy.AddMessage("Making closed multipatch volumes for maximum range threat volumes.")
arcpy.EncloseMultiPatch_3d(QA_MaxZone_FeaturesFromCityE, QA_MaxZone_CE_enclosed, g_ESRI_variable_39)

# Process: Int3D Max Corridor Plus Elev
arcpy.AddMessage("Intersecting dome segments with bases and maximum range threat volumes.")
arcpy.Intersect3D_3d(DomePlusGround, Flight_Corridor_Dangerous, QA_MaxZone_CE_enclosed, g_ESRI_variable_32)

# Process: Is Closed 3D
arcpy.AddMessage("Testing for multipatch closure of dangerous flight corridor features.")
arcpy.IsClosed3D_3d(QA_MaxZone_CE_enclosed)

# Process: Detect non-closed volumes
arcpy.AddMessage("Creating error features for un-closed dangerous flight corridor features.")
arcpy.ShowNonClosedVolumes_RangeDomePyTools(QA_MaxZone_CE_enclosed, FlightCorridor_Dangerous_error)


# Process: Enclose Multipatch (2)
arcpy.AddMessage("Making closed multipatch volumes for lethal range threat volumes. Note: This step takes some time.")
arcpy.EncloseMultiPatch_3d(QA_MinZone_CE_enclosed_Featu, QA_MinZone_CE_enclosed, g_ESRI_variable_39)

# Process: Int3D Min Corridor Plus Elev
arcpy.AddMessage("Intersecting dome segments with bases and lethal range threat volumes. Note: This step takes some time.")
arcpy.Intersect3D_3d(DomePlusGround, Flight_Corridor_Lethal, QA_MinZone_CE_enclosed, g_ESRI_variable_32)

# Process: Is Closed 3D
arcpy.AddMessage("Testing for multipatch closure of lethal flight corridor features.")
arcpy.IsClosed3D_3d(QA_MinZone_CE_enclosed)

# Process: Detect non-closed volumes
arcpy.AddMessage("Creating error features for un-closed lethal flight corridor features.")
arcpy.ShowNonClosedVolumes_RangeDomePyTools(QA_MinZone_CE_enclosed, FlightCorridor_Lethal_error)

# Process: Make and Append warning images for "Dangerous" error features
arcpy.AddMessage("Adding warning image attachments to dangerous flight corridor features.")
make_append_warning_images(FlightCorridor_Dangerous_error, WarningDangerous_png)

# Process: Make and Append warning images for "Lethal" error features
arcpy.AddMessage("Adding warning image attachments to lethal flight corridor features.")
make_append_warning_images(FlightCorridor_Lethal_error, WarningLethal_png)

#Clean up in_memory items
#arcpy.AddMessage("Cleaning up in_memory items")
#in_mem_cleanup_list = ["Weapon_Positions_3D","Lethal_3D_Buffer_Zone","Corridor_Lethal","QA_MinZone_CE_enclosed_Featu","QA_MinZone_CE_enclosed_Featu_MPoints","Max_3D_Buffer_Zone","Corridor_Max","QA_MaxZone_FeaturesFromCityE","Visibility_Raster__Yes_No_","Visibility_Raster__RTG_Height_","Visibility_Raster__ABS_Height_","Ground_Zone__Mesh_","DomePlusGround","v2D_Zone","v2D_Zone__SinglePart_","v2D_Zone__Simplified_","QA_MaxZone_FeaturesFromCityE","Corridor_Buffer","CorridorBuffer_shp","CorridorVolume","DomePlusGround","QA_MaxZone_CE_enclosed","QA_MinZone_CE_enclosed"]
#for in_mem_item in in_mem_cleanup_list:
#    arcpy.Delete_management(in_mem_item)

arcpy.AddMessage("Range Dome Analysis complete.")

