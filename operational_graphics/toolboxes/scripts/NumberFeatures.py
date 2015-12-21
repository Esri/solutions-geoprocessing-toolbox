# coding: utf-8
#------------------------------------------------------------------------------
# Copyright 2015 Esri
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
# This tool will number features within a point feature class spatially from left to right,
# top to bottom for a selected area.
#
# ==================================================
# HISTORY:
#
# 8/25/2015 - mf - Needed to update script for non-ArcMap/Pro testing environment
#
# ==================================================

import os, sys, math, traceback
import arcpy
from arcpy import env
from arcpy import sa
import Utilities

# Read in the Parameters
areaToNumber = arcpy.GetParameterAsText(0)
pointFeatures = arcpy.GetParameterAsText(1)
numberingField = arcpy.GetParameterAsText(2)
outputFeatureClass = arcpy.GetParameterAsText(3)

DEBUG = True
appEnvironment = None
mxd, df, aprx, mp, mapList = None, None, None, None, None

def labelFeatures(layer, field):

    ''' set up labeling for layer '''
    if appEnvironment == "ARCGIS_PRO":
        if layer.supports("SHOWLABELS"):
            for lblclass in layer.listLabelClasses():
                lblclass.visible = True
                lblclass.expression = " [" + str(field) + "]"
            layer.showLabels = True
    elif appEnvironment == "ARCMAP":
        if layer.supports("LABELCLASSES"):
            for lblclass in layer.labelClasses:
                lblclass.showClassLabels = True
                lblclass.expression = " [" + str(field) + "]"
            layer.showLabels = True
            arcpy.RefreshActiveView()
    else:
        pass # if returns "OTHER"

def findLayerByName(layerName):
    #UPDATE
    if appEnvironment == "ARCGIS_PRO":
    #if gisVersion == "1.0": #Pro:
        if DEBUG == True:
            arcpy.AddMessage("Pro labeling for " + layerName + "...")
        for layer in mapList.listLayers():
            if layer.name == layerName:
                arcpy.AddMessage("Found matching layer [" + layer.name + "]")
                return layer
            else:
                arcpy.AddMessage("Incorrect layer: [" + layer.name + "]")

    #else:
    elif appEnvironment == "ARCMAP":
        if DEBUG == True: arcpy.AddMessage("Map labeling for " + layerName + "...")

        for layer in arcpy.mapping.ListLayers(mxd):
            if layer.name == layerName:
                arcpy.AddMessage("Found matching layer [" + layer.name + "]")
                return layer
            else:
                arcpy.AddMessage("Incorrect layer: [" + layer.name + "]")
    else:
        arcpy.AddMessage("Non-map environment, no layers to find...")


def GetApplication():
    '''Return app environment as ARCMAP, ARCGIS_PRO, OTHER'''
    try:
        from arcpy import mp
        return "ARCGIS_PRO"
    except ImportError:
        try:
            from arcpy import mapping
            mxd = arcpy.mapping.MapDocument("CURRENT")
            return "ARCMAP"
        except:
            return "OTHER"



def main():
    ''' main '''
    #UPDATE
    # Create a feature layer from the input point features if it is not one already
    #df = arcpy.mapping.ListDataFrames(mxd)[0]
    pointFeatureName = os.path.basename(pointFeatures)
    layerExists = False

    try:
        # Check that area to number is a polygon
        descArea = arcpy.Describe(areaToNumber)
        areaGeom = descArea.shapeType
        arcpy.AddMessage("Shape type: " + str(areaGeom))
        if (descArea.shapeType != "Polygon"):
            raise Exception("ERROR: The area to number must be a polygon.")

        gisVersion = arcpy.GetInstallInfo()["Version"]
        global appEnvironment
        appEnvironment = Utilities.GetApplication()
        if DEBUG == True: arcpy.AddMessage("App environment: " + appEnvironment)

        global mxd
        global df
        global aprx
        global mp
        global mapList
        # mxd, df, aprx, mp = None, None, None, None
        #if gisVersion == "1.0": #Pro:
        if appEnvironment == "ARCGIS_PRO":
            from arcpy import mp
            aprx = arcpy.mp.ArcGISProject("CURRENT")
            mapList = aprx.listMaps()[0]
            for lyr in mapList.listLayers():
                if lyr.name == pointFeatureName:
                    layerExists = True
        #else:
        if appEnvironment == "ARCMAP":
            from arcpy import mapping
            mxd = arcpy.mapping.MapDocument('CURRENT')
            df = arcpy.mapping.ListDataFrames(mxd)[0]
            for lyr in arcpy.mapping.ListLayers(mxd):
                if lyr.name == pointFeatureName:
                    layerExists = True

        if layerExists == False:
            arcpy.MakeFeatureLayer_management(pointFeatures, pointFeatureName)
        else:
            pointFeatureName = pointFeatures

        # Select all the points that are inside of area
        arcpy.AddMessage("Selecting points from (" + str(os.path.basename(pointFeatureName)) +\
                         ") inside of the area (" + str(os.path.basename(areaToNumber)) + ")")
        selectionLayer = arcpy.SelectLayerByLocation_management(pointFeatureName, "INTERSECT",
                                                                areaToNumber, "#", "NEW_SELECTION")
        if DEBUG == True:
            arcpy.AddMessage("Selected " + str(arcpy.GetCount_management(pointFeatureName).getOutput(0)) + " points")

        # If no output FC is specified, then set it a temporary one, as this will be copied to the input and then deleted.
        # Sort layer by upper right across and then down spatially,
        overwriteFC = False
        global outputFeatureClass
        if outputFeatureClass == "":
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
            overwriteFC = os.path.join(os.path.sep, desc.path, pointFeatureName)
            fields = (numberingField, "SHAPE@")
            overwriteCursor = arcpy.da.UpdateCursor(overwriteFC, fields)
            for overwriteRow in overwriteCursor:
                sortedPointsCursor = arcpy.da.SearchCursor(outputFeatureClass, fields)
                for sortedRow in sortedPointsCursor:
                    if sortedRow[1].equals(overwriteRow[1]):
                        overwriteRow[0] = sortedRow[0]
                overwriteCursor.updateRow(overwriteRow)
            arcpy.Delete_management(outputFeatureClass)

            #UPDATE
            #if layerExists == False:
                #layerToAdd = arcpy.mapping.Layer(pointFeatureName)
                #arcpy.mapping.AddLayer(df, layerToAdd, "AUTO_ARRANGE")
            targetLayerName = pointFeatureName
        else:
            #UPDATE
            #layerToAdd = arcpy.mapping.Layer(outputFeatureClass)
            #arcpy.mapping.AddLayer(df, layerToAdd, "AUTO_ARRANGE")
            targetLayerName = os.path.basename(outputFeatureClass)


        # Get and label the output feature
        if appEnvironment == "ARCGIS_PRO":
            results = arcpy.MakeFeatureLayer_management(outputFeatureClass, targetLayerName).getOutput(0)
            mapList.addLayer(results, "AUTO_ARRANGE")
            layer = findLayerByName(targetLayerName)
            if(layer):
                labelFeatures(layer, numberingField)
        elif appEnvironment == "ARCMAP":
            arcpy.AddMessage("Adding features to map (" + str(targetLayerName) + ")...")
            arcpy.MakeFeatureLayer_management(outputFeatureClass, targetLayerName)
            layer = arcpy.mapping.Layer(targetLayerName)
            arcpy.mapping.AddLayer(df, layer, "AUTO_ARRANGE")
            arcpy.AddMessage("Labeling output features (" + str(targetLayerName) + ")...")
            layer = findLayerByName(targetLayerName)
            if (layer):
                labelFeatures(layer, numberingField)
        else:
            arcpy.AddMessage("Non-map application, skipping labeling...")


        arcpy.SetParameter(3, outputFeatureClass)


    except arcpy.ExecuteError:
        # Get the tool error messages
        msgs = arcpy.GetMessages()
        arcpy.AddError(msgs)
        print(msgs)

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
        print(pymsg + "\n")
        print(msgs)

# MAIN =============================================
if __name__ == "__main__":
    main()
