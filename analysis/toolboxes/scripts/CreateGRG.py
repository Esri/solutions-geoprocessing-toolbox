import os, sys, math, traceback
import arcpy
# Read in the parameters
templateExtent = arcpy.GetParameterAsText(0)
cellWidth = arcpy.GetParameterAsText(1)
cellHeight = arcpy.GetParameterAsText(2)
gridSize = arcpy.GetParameterAsText(3)
outputFeatureClass = arcpy.GetParameterAsText(4)
tempOutput = "in_memory" + "\\" + "tempFishnetGrid"

def labelFeatures(layer, field):
    if layer.supports("LABELCLASSES"):
        for lblclass in layer.labelClasses:
            lblclass.showClassLabels = True
            lblclass.expression = " [" + str(field) + "]"
        layer.showLabels = True
        arcpy.RefreshActiveView()

def findLayerByName(layerName):
    for layer in arcpy.mapping.ListLayers(mxd):
        if layer.name == layerName:
            return layer

mxd = arcpy.mapping.MapDocument('CURRENT')
df = arcpy.mapping.ListDataFrames(mxd)[0]

# From the template extent, get the origin, y axis, and opposite corner corrdinates
extents = str.split(str(templateExtent))
originCoordinate = extents[0] + " " + extents[1]
yAxisCoordinate = extents[0] + " " + extents[1]
oppCornerCoordinate = extents[2] + " " + extents[3]

# If grid size is drawn on the map, use this instead of cell width and cell height
if float(cellWidth) == 0 and float(cellHeight) == 0:
    descGrid = arcpy.Describe(gridSize)
    gridExtent = (arcpy.Describe(gridSize)).extent
    cellWidth = gridExtent.XMax - gridExtent.XMin
    cellHeight = gridExtent.YMax - gridExtent.YMin

# Import the custom toolbox with the fishnet tool in it, and run this. This had to be added to a model,
# because of a bug, which will now allow you to pass variables to the Create Fishnet tool.
toolboxPath = os.path.dirname(os.path.dirname(arcpy.env.workspace)) + "\\toolboxes\VillageClearing.tbx"
arcpy.ImportToolbox(toolboxPath, "VillageClearing")
arcpy.AddMessage("Creating Fishnet Grid")
arcpy.CreateFishnet_VillageClearing(tempOutput, originCoordinate, yAxisCoordinate, str(cellWidth), str(cellHeight), 0, 0, oppCornerCoordinate, "NO_LABELS", templateExtent, "POLYGON")

# Sort the grid upper left to lower right, and delete the in memory one
arcpy.AddMessage("Sorting the grid for labeling")
arcpy.Sort_management(tempOutput, outputFeatureClass, [["Shape", "ASCENDING"]], "UL")
arcpy.Delete_management("in_memory")

# Add a field which will be used to add the grid labels
arcpy.AddMessage("Adding field for labeling the grid")
gridField = "Grid"
arcpy.AddField_management(outputFeatureClass, gridField, "TEXT")

# Number the fields
arcpy.AddMessage("Numbering the grids")
letter = 'A'
number = 1
lastY = -9999
cursor = arcpy.UpdateCursor(outputFeatureClass)
for row in cursor:
    yPoint = row.getValue("SHAPE").firstPoint.Y
    if (lastY != yPoint) and (lastY != -9999):
        letter = chr(ord(letter) + 1)
        number = 1
    lastY = yPoint
    row.setValue(gridField, str(letter) + str(number))
    cursor.updateRow(row)
    number += 1


# Get and label the output feature
layerToAdd = arcpy.mapping.Layer(outputFeatureClass)
arcpy.mapping.AddLayer(df, layerToAdd, "AUTO_ARRANGE")
targetLayerName = os.path.basename(outputFeatureClass)
layer = findLayerByName(targetLayerName)

if(layer):
    arcpy.AddMessage("Labeling grids")
    labelFeatures(layer, gridField)

# Apply symbology to the GRG layer
symbologyPath = os.path.dirname(arcpy.env.workspace) + "\\Layers\GRG.lyr"
arcpy.ApplySymbologyFromLayer_management(layer, symbologyPath)