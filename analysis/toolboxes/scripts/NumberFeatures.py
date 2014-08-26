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
# 
# ==================================================
# NumberFeatures.py
# --------------------------------------------------
# Built on ArcGIS
# ==================================================
# 
# <Description>
#
# 

import os, sys, math, traceback
import arcpy

# Read in the Parameters
areaToNumber = arcpy.GetParameterAsText(0)
pointFeatures = arcpy.GetParameterAsText(1)
numberingField = arcpy.GetParameterAsText(2)
outputFeatureClass = arcpy.GetParameterAsText(3)

def labelFeatures(layer, field):
    if layer.supports("LABELCLASSES"):
        for lblclass in layer.labelClasses:
            lblclass.showClassLabels = True
            lblclass.expression = " [" + str(field) + "]"
        layer.showLabels = True 
        arcpy.RefreshActiveView()  

def findLayerByName(layerName):
    #TODO: Pro updates for arcpy.mapping
    for layer in arcpy.mapping.ListLayers(mxd):        
        if layer.name == layerName:
            arcpy.AddMessage("Found matching layer [" + layer.name + "]")
            return layer
        else:
            arcpy.AddMessage("Incorrect layer: [" + layer.name + "]")

# Create a feature layer from the input point features if it is not one already
#TODO: Pro updates for arcpy.mapping
mxd = arcpy.mapping.MapDocument('CURRENT')
df = arcpy.mapping.ListDataFrames(mxd)[0]

pointFeatureName = os.path.basename(pointFeatures)
layerExists = False

#TODO: Pro updates for arcpy.mapping
for lyr in arcpy.mapping.ListLayers(mxd):
    if lyr.name == pointFeatureName:
        layerExists = True
        
if layerExists == False:
    arcpy.MakeFeatureLayer_management(pointFeatures, pointFeatureName)
else:
    pointFeatureName = pointFeatures

# Select all the points that are inside of area
arcpy.AddMessage("Selecting points inside of the area")
selectionLayer = arcpy.SelectLayerByLocation_management(pointFeatureName, "intersect", areaToNumber)

# If no output FC is specified, then set it a temporary one, as this will be copied to the input and then deleted.
# Sort layer by upper right across and then down spatially, 
overwriteFC = False; 
if (outputFeatureClass == ""):
    outputFeatureClass = "tempSortedPoints"
    overwriteFC = True;
arcpy.AddMessage("Sorting the selected points geographically, right to left, top to bottom")
arcpy.Sort_management(selectionLayer, outputFeatureClass, [["Shape", "ASCENDING"]])

# Number the fields
arcpy.AddMessage("Numbering the fields")
i = 1   
cursor = arcpy.UpdateCursor(outputFeatureClass)
for row in cursor:
    row.setValue(numberingField, i)
    cursor.updateRow(row)
    i += 1
    
# Clear the selection
arcpy.AddMessage("Clearing the selection")
arcpy.SelectLayerByAttribute_management(pointFeatureName, "CLEAR_SELECTION")

# Overwrite the Input Point Features, and then delete the temporary output feature class
targetLayerName = ""
if (overwriteFC):
    arcpy.AddMessage("Copying the features to the input, and then deleting the temporary feature class")
    desc = arcpy.Describe(pointFeatureName)
    arcpy.CopyFeatures_management(outputFeatureClass, desc.path + "\\" + pointFeatureName)
    arcpy.Delete_management(outputFeatureClass)
    if layerExists == False:
        #TODO: Pro updates for arcpy.mapping
        layerToAdd = arcpy.mapping.Layer(pointFeatureName)
        arcpy.mapping.AddLayer(df, layerToAdd, "AUTO_ARRANGE")
    targetLayerName = pointFeatureName
else:
    #TODO: Pro updates for arcpy.mapping
    layerToAdd = arcpy.mapping.Layer(outputFeatureClass)
    arcpy.mapping.AddLayer(df, layerToAdd, "AUTO_ARRANGE")
    targetLayerName = os.path.basename(outputFeatureClass)
    
# Get and label the output feature
layer = findLayerByName(targetLayerName)
if(layer):
    labelFeatures(layer, numberingField)