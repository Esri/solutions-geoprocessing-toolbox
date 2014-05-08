# Author: Esri
# Date:   September 2012
#
# Purpose: Creates polygon fishnets around input features.
#          A common use for this is dividing irregular polygons into regular-shaped study areas.
#          Fishnets will have minimum width fitting each input feature or group.
#          Cell rows are counted along the fishnet long axis, columns along the short axis.

import arcpy
import math
import os

# Input features
in_features = arcpy.GetParameterAsText(0)

# Output features
out_features = arcpy.GetParameterAsText(1)

# Optional input group strategy
group_option = arcpy.GetParameterAsText(2)

# Fields used by group strategy
group_fields = arcpy.GetParameterAsText(3)

# Fishnet cell width
cell_width = arcpy.GetParameterAsText(4)

# Fishnet cell height
cell_height = arcpy.GetParameterAsText(5)
                                       
# Cell row count if not specifying cell size
number_rows = arcpy.GetParameterAsText(6)
                                       
# Cell column count if not specifying cell size
number_columns = arcpy.GetParameterAsText(7)
                                       
# Optionally create a label point feature class
labels = arcpy.GetParameterAsText(8)

# Housekeeping
arcpy.env.overWriteOutput = True
sR = arcpy.Describe(in_features).spatialReference
arcpy.env.outputCoordinateSystem = sR
arcpy.env.workspace = os.path.dirname(out_features)
                                    
# Functions

# Rotate a point about another point
def RotatePoint(inPoint,centrePoint,angle=0):
    angle = math.radians(angle)
    x = float(inPoint.X) - float(centrePoint.X)
    y = float(inPoint.Y) - float(centrePoint.Y)
    xr = (x * math.cos(angle)) - (y * math.sin(angle)) + float(centrePoint.X)
    yr = (x * math.sin(angle)) + (y * math.cos(angle)) + float(centrePoint.Y)
    return arcpy.Point(xr,yr)

# Rotate a (single part) polygon about a point
def RotatePolygon(inPoly,centrePoint,angle=0):
    arr = arcpy.Array()
    for pt in inPoly.getPart(0):
        arr.add(RotatePoint(pt,centrePoint,angle))
    return arcpy.Polygon(arr)

# Process the data
scratchName = arcpy.CreateScratchName("MBG","ByWidth","FeatureClass")
arcpy.MinimumBoundingGeometry_management(in_features,scratchName,"RECTANGLE_BY_WIDTH",group_option,group_fields,"MBG_FIELDS")
arcpy.DeleteField_management(scratchName,["MBG_Width","MBG_Length","ORIG_FID"])
arcpy.CreateFeatureclass_management(os.path.dirname(out_features),\
                                    os.path.basename(out_features),"POLYGON",\
                                    template=scratchName,\
                                    spatial_reference=sR)
cur = arcpy.da.InsertCursor(out_features,["SHAPE@","MBG_Orientation"])
if labels == "LABELS":
    arcpy.CreateFeatureclass_management(os.path.dirname(out_features),\
                                        os.path.basename(out_features)+"_label","POINT",\
                                        spatial_reference=sR)
for row in arcpy.da.SearchCursor(scratchName,["OID@","SHAPE@","MBG_Orientation"]):
    oid = row[0]
    #arcpy.AddMessage("\nProcessing polygon " + str(oid))
    mbgPoly = row[1]
    orientation = float(row[2])
    pivotPoint = mbgPoly.firstPoint
    origin_coord = str(pivotPoint.X) + ' ' + str(pivotPoint.Y)
    opposite_corner_coord = None
    orthogonalPoly = RotatePolygon(mbgPoly,pivotPoint,orientation)
    opposite_corner = str(orthogonalPoly.extent.XMax) + ' ' + str(orthogonalPoly.extent.YMax)
    yCoord = str(pivotPoint.X) + ' ' + str(pivotPoint.Y + 1.0)
    scratchName2 = arcpy.CreateScratchName("OrthogonalFishNet",str(oid),"FeatureClass")
    arcpy.CreateFishnet_management(scratchName2,origin_coord,yCoord,cell_width,cell_height,number_rows,number_columns,labels=labels,template=orthogonalPoly.extent,geometry_type="POLYGON")
    #arcpy.CreateFishnet_management(scratchName2,origin_coord,yCoord,cell_width,cell_height,number_rows,number_columns,opposite_corner,labels=labels,geometry_type="POLYGON")
    for cell in arcpy.da.SearchCursor(scratchName2,["OID@","SHAPE@"]):
        #arcpy.AddMessage("Processing fishnet cell..."  + str(cell[0]))
        outPoly = RotatePolygon(cell[1],pivotPoint,0-orientation)
        cur.insertRow([outPoly,orientation])
    arcpy.Delete_management(scratchName2)
    if labels == "LABELS":
        del cur #Otherwise two InsertCursors in the same workspace requires arcpy.da.Editor
        lcur = arcpy.da.InsertCursor(out_features+"_label",["SHAPE@"])
        for label in arcpy.da.SearchCursor(scratchName2+"_label",["SHAPE@"]):
            lcur.insertRow([arcpy.PointGeometry(RotatePoint(label[0].firstPoint,pivotPoint,0-orientation),sR)])
        arcpy.Delete_management(scratchName2+"_label")
        del lcur
        cur = arcpy.da.InsertCursor(out_features,["SHAPE@","MBG_Orientation"])
arcpy.Delete_management(scratchName)
del cur
arcpy.AddMessage("\nDone")

