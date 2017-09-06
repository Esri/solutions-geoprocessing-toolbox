# coding: utf-8
'''
------------------------------------------------------------------------------
 Copyright 2017 Esri
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
------------------------------------------------------------------------------
 ==================================================
 NumberFeatures_new.py
 --------------------------------------------------
 requirements: ArcGIS X.X, Python 2.7 or Python 3.x
 author: ArcGIS Solutions
 contact: support@esri.com
 company: Esri
 ==================================================
 description: 
 GRG Tool logic module. 
 Supports ClearingOperationsTools.pyt
 ==================================================
 history:
 9/6/2017 - mf - original coding
 ==================================================
'''


import os, sys, math, traceback
import arcpy
from arcpy import env
from arcpy import sa
import Utilities

DEBUG = True
appEnvironment = None
mxd, df, aprx, mp, mapList = None, None, None, None, None

class NumberFeatures(object):
    '''
    '''
    def __init__(self):
        '''
        Number Features constructor
        '''
        self.label = "Number Features"
        self.description = "Number input point features within a selected area."

    def getParameterInfo(self):
        '''
        Define parameter definitions
        '''

        return []

    def updateParameters(self, parameters):
        '''
        Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed.
        '''
        return

    def updateMessages(self, parameters):
        '''
        '''
        return

    def execute(self, parameters, messages):
        '''
        '''
        # areaToNumber = parameters(0)
        # pointFeatures = parameters(1)
        # numberingField = parameters(2)
        # outputFeatureClass = parameters(3)
        # 
        # output_fc = main(areaToNumber,
        #                  pointFeatures,
        #                  numberingField,
        #                  outputFeatureClass)
        
        return #output_fc
    
    # def main(areaToNumber,
    #          pointFeatures,
    #          numberingField,
    #          outputFeatureClass):
    #     ''' main '''
    #     #UPDATE
    #     # Create a feature layer from the input point features if it is not one already
    #     #df = arcpy.mapping.ListDataFrames(mxd)[0]
    #     pointFeatureName = os.path.basename(pointFeatures)
    #     layerExists = False
    # 
    #     try:
    #         # Check that area to number is a polygon
    #         descArea = arcpy.Describe(areaToNumber)
    #         areaGeom = descArea.shapeType
    #         arcpy.AddMessage("Shape type: " + str(areaGeom))
    #         if (descArea.shapeType != "Polygon"):
    #             raise Exception("ERROR: The area to number must be a polygon.")
    # 
    #         gisVersion = arcpy.GetInstallInfo()["Version"]
    #         global appEnvironment
    #         appEnvironment = Utilities.GetApplication()
    #         if DEBUG == True: arcpy.AddMessage("App environment: " + appEnvironment)
    # 
    #         global mxd
    #         global df
    #         global aprx
    #         global mp
    #         global mapList
    #         # mxd, df, aprx, mp = None, None, None, None
    #         #if gisVersion == "1.0": #Pro:
    #         if appEnvironment == "ARCGIS_PRO":
    #             from arcpy import mp
    #             aprx = arcpy.mp.ArcGISProject("CURRENT")
    #             mapList = aprx.listMaps()[0]
    #             for lyr in mapList.listLayers():
    #                 if lyr.name == pointFeatureName:
    #                     layerExists = True
    #         #else:
    #         if appEnvironment == "ARCMAP":
    #             from arcpy import mapping
    #             mxd = arcpy.mapping.MapDocument('CURRENT')
    #             df = arcpy.mapping.ListDataFrames(mxd)[0]
    #             for lyr in arcpy.mapping.ListLayers(mxd):
    #                 if lyr.name == pointFeatureName:
    #                     layerExists = True
    # 
    #         if layerExists == False:
    #             arcpy.MakeFeatureLayer_management(pointFeatures, pointFeatureName)
    #         else:
    #             pointFeatureName = pointFeatures
    # 
    #         # Select all the points that are inside of area
    #         arcpy.AddMessage("Selecting points from (" + str(os.path.basename(pointFeatureName)) +\
    #                          ") inside of the area (" + str(os.path.basename(areaToNumber)) + ")")
    #         selectionLayer = arcpy.SelectLayerByLocation_management(pointFeatureName, "INTERSECT",
    #                                                                 areaToNumber, "#", "NEW_SELECTION")
    #         if DEBUG == True:
    #             arcpy.AddMessage("Selected " + str(arcpy.GetCount_management(pointFeatureName).getOutput(0)) + " points")
    # 
    #         # If no output FC is specified, then set it a temporary one, as this will be copied to the input and then deleted.
    #         # Sort layer by upper right across and then down spatially,
    #         overwriteFC = False
    #         global outputFeatureClass
    #         if outputFeatureClass == "":
    #             outputFeatureClass = g_ESRI_variable_1
    #             overwriteFC = True;
    #         arcpy.AddMessage("Sorting the selected points geographically, right to left, top to bottom")
    #         arcpy.Sort_management(selectionLayer, outputFeatureClass, [["Shape", "ASCENDING"]])
    # 
    # 
    #         # Number the fields
    #         arcpy.AddMessage("Numbering the fields")
    #         i = 1
    #         cursor = arcpy.UpdateCursor(outputFeatureClass)
    #         for row in cursor:
    #             row.setValue(numberingField, i)
    #             cursor.updateRow(row)
    #             i += 1
    # 
    # 
    #         # Clear the selection
    #         arcpy.AddMessage("Clearing the selection")
    #         arcpy.SelectLayerByAttribute_management(pointFeatureName, "CLEAR_SELECTION")
    # 
    # 
    #         # Overwrite the Input Point Features, and then delete the temporary output feature class
    #         targetLayerName = ""
    #         if (overwriteFC):
    #             arcpy.AddMessage("Copying the features to the input, and then deleting the temporary feature class")
    #             desc = arcpy.Describe(pointFeatures)
    #             if hasattr(desc, "layer"):
    #               overwriteFC = desc.layer.catalogPath
    #             else:
    #               overwriteFC = desc.catalogPath
    #             fields = (numberingField, "SHAPE@")
    #             overwriteCursor = arcpy.da.UpdateCursor(overwriteFC, fields)
    #             for overwriteRow in overwriteCursor:
    #                 sortedPointsCursor = arcpy.da.SearchCursor(outputFeatureClass, fields)
    #                 for sortedRow in sortedPointsCursor:
    #                     if sortedRow[1].equals(overwriteRow[1]):
    #                         overwriteRow[0] = sortedRow[0]
    #                 overwriteCursor.updateRow(overwriteRow)
    #             arcpy.Delete_management(outputFeatureClass)
    # 
    #             #UPDATE
    #             #if layerExists == False:
    #                 #layerToAdd = arcpy.mapping.Layer(pointFeatureName)
    #                 #arcpy.mapping.AddLayer(df, layerToAdd, "AUTO_ARRANGE")
    #             targetLayerName = pointFeatureName
    #         else:
    #             #UPDATE
    #             #layerToAdd = arcpy.mapping.Layer(outputFeatureClass)
    #             #arcpy.mapping.AddLayer(df, layerToAdd, "AUTO_ARRANGE")
    #             targetLayerName = os.path.basename(outputFeatureClass)
    # 
    # 
    #         # Get and label the output feature
    #         if appEnvironment == "ARCGIS_PRO":
    #             
    #             #params = arcpy.GetParameterInfo()
    #             ##get the symbology from the NumberedStructures.lyr
    #             #scriptPath = sys.path[0]
    #             #arcpy.AddMessage(scriptPath)
    #             #layerFilePath = os.path.join(scriptPath,r"commondata\userdata\NumberedStructures.lyrx")            
    #             #params[3].symbology = layerFilePath
    #             #arcpy.AddMessage("Applying Symbology from {0}".format(layerFilePath))
    #             
    #             arcpy.AddMessage("Applying symbology on the script tool based on best practice")
    #            
    #         elif appEnvironment == "ARCMAP":
    #             #arcpy.AddMessage("Adding features to map (" + str(targetLayerName) + ")...")
    #             
    #             #arcpy.MakeFeatureLayer_management(outputFeatureClass, targetLayerName)
    #             
    #             # create a layer object
    #             #layer = arcpy.mapping.Layer(targetLayerName)            
    #             
    #             # get the symbology from the NumberedStructures.lyr
    #             #layerFilePath = os.path.join(os.getcwd(),r"data\Layers\NumberedStructures.lyr")
    #             #layerFilePath = os.path.join(os.path.dirname(os.path.dirname(__file__)),r"layers\NumberedStructures.lyr")
    #             
    #             # apply the symbology to the layer
    #             #arcpy.ApplySymbologyFromLayer_management(layer, layerFilePath)
    #             
    #             # add layer to map
    #             #arcpy.mapping.AddLayer(df, layer, "AUTO_ARRANGE")
    #             
    #             # find the target layer in the map
    #             #mapLyr = arcpy.mapping.ListLayers(mxd, targetLayerName)[0]  
    # 
    #             #arcpy.AddMessage("Labeling output features (" + str(targetLayerName) + ")...")
    #             # Work around needed as ApplySymbologyFromLayer_management does not honour labels
    #             #labelLyr = arcpy.mapping.Layer(layerFilePath)
    #             # copy the label info from the source to the map layer
    #             #mapLyr.labelClasses = labelLyr.labelClasses
    #             # turn labels on
    #             #mapLyr.showLabels = True
    #             arcpy.AddMessage("Applying symbology on the script tool based on best practice")
    #         else:
    #             arcpy.AddMessage("Non-map application, skipping labeling...")
    # 
    # 
    #         #arcpy.SetParameter(3, outputFeatureClass)
    #         return outputFeatureClass
    # 
    #     except arcpy.ExecuteError:
    #         # Get the tool error messages
    #         msgs = arcpy.GetMessages()
    #         arcpy.AddError(msgs)
    #         print(msgs)
    # 
    #     except:
    #         # Get the traceback object
    #         tb = sys.exc_info()[2]
    #         tbinfo = traceback.format_tb(tb)[0]
    # 
    #         # Concatenate information together concerning the error into a message string
    #         pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    #         msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"
    # 
    #         # Return python error messages for use in script tool or Python Window
    #         arcpy.AddError(pymsg)
    #         arcpy.AddError(msgs)
    # 
    #         # Print Python error messages for use in Python / Python Window
    #         print(pymsg + "\n")
    #         print(msgs)
