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
 Number Features Tool logic module. 
 Supports ClearingOperationsTools.pyt
 ==================================================
 history:
 9/6/2017 - mf - original coding/transfer from NumberFeatures.py
 ==================================================
'''


import os
import sys
import traceback
import arcpy
from . import Utilities

class NumberFeatures(object):
    '''
    Number input features within a specified area.
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
        input_area_features = arcpy.Parameter(name='input_area_features',
                                              displayName='Input Area to Number',
                                              direction='Input',
                                              datatype='GPFeatureRecordSetLayer',
                                              parameterType='Required',
                                              enabled=True,
                                              multiValue=False)
        input_area_features.value = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                 "layers", "NumberFeaturesAreaInput.lyr")

        input_number_features = arcpy.Parameter(name='input_point_features',
                                               displayName='Features to Number',
                                               direction='Input',
                                               datatype='GPFeatureLayer',
                                               parameterType='Required',
                                               enabled=True,
                                               multiValue=False)

        field_to_number = arcpy.Parameter(name='field_to_number',
                                          displayName='Field to Number',
                                          direction='Input',
                                          datatype='Field',
                                          parameterType='Optional',
                                          enabled=True,
                                          multiValue=False)
        field_to_number.filter.list = ['Short', 'Long', 'Double', 'Single']
        field_to_number.parameterDependencies = [input_number_features.name]

        output_features= arcpy.Parameter(name='output_features',
                                         displayName='Output Numbered Features',
                                         direction='Output',
                                         datatype='DEFeatureClass',
                                         parameterType='Optional',
                                         enabled=True,
                                         multiValue=False)
        #output_features.value = r"%scratchGDB%/numbered_features"
        output_features.symbology = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                 "layers", "NumberedStructures.lyr")

        return [input_area_features,
                input_number_features,
                field_to_number,
                output_features]

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

        output_fc = self.NumberFeatures(parameters[0].value,
                                        parameters[1].value,
                                        parameters[2].value,
                                        parameters[3].value)

        return output_fc


    def NumberFeatures(self,
                       areaToNumber,
                       pointFeatures,
                       numberingField,
                       outputFeatureClass):
        ''' copied and modified from original NumberFeatures.py '''
        g_ESRI_variable_1 = r'%scratchGDB%\tempSortedPoints'

        arcpy.CopyFeatures_management(areaToNumber, os.path.join("in_memory","areaToNumber"))
        areaToNumber = os.path.join("in_memory","areaToNumber")
        arcpy.AddMessage("outputFeatureClass: {0}".format(outputFeatureClass))

        DEBUG = True
        appEnvironment = None
        mxd, df, aprx, mp, mapList = None, None, None, None, None
        pointFeatureName = os.path.basename(str(pointFeatures))
        layerExists = False
        try:
            # Check that area to number is a polygon
            descArea = arcpy.Describe(areaToNumber)
            areaGeom = descArea.shapeType
            arcpy.AddMessage("Shape type: " + str(areaGeom))
            if (descArea.shapeType != "Polygon"):
                raise Exception("ERROR: The area to number must be a polygon.")

            #Checking the version of the Desktop Application
            appEnvironment = Utilities.GetApplication()
            if DEBUG == True: arcpy.AddMessage("App environment: " + appEnvironment)

            #Getting the layer name from the Table of Contents
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
            if areaToNumber:
                arcpy.AddMessage("Selecting points from {0} inside of the area {1}".format(pointFeatureName, areaToNumber))
            else:
                arcpy.AddMessage("Selecting points from {0} inside of the area {1}".format(pointFeatureName, areaToNumber.name))

            selectionLayer = arcpy.SelectLayerByLocation_management(pointFeatureName, "INTERSECT",
                                                                    areaToNumber, "#", "NEW_SELECTION")
            if DEBUG == True:
                arcpy.AddMessage("Selected " + str(arcpy.GetCount_management(pointFeatureName).getOutput(0)) + " points")

            # If no output FC is specified, then set it a temporary one, as this will be copied to the input and then deleted.
            # Sort layer by upper right across and then down spatially,
            overwriteFC = False
            if not outputFeatureClass:
                outputFeatureClass = g_ESRI_variable_1
                overwriteFC = True

            arcpy.AddMessage("Sorting the selected points geographically, left to right, top to bottom")
            arcpy.Sort_management(pointFeatureName, outputFeatureClass, [["Shape", "ASCENDING"]])

            #global numberingField
            if numberingField is None or numberingField == "":
                fnames = [field.name for field in arcpy.ListFields(outputFeatureClass)]
                addfield = "Number"
                if addfield in fnames:
                    arcpy.AddMessage("Number field is already used")
                    numberingField = "Number"
                else:
                    arcpy.AddMessage("Add One")
                    arcpy.AddMessage("Adding Number field because no input field was given")
                    arcpy.AddField_management(outputFeatureClass,"Number","SHORT")
                    numberingField = "Number"
            else:
                pass

            # Number the fields
            arcpy.AddMessage("Numbering the fields")
            i = 1
            cursor = arcpy.UpdateCursor(outputFeatureClass) # Object: Error in parsing arguments for UpdateCursor
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
                desc = arcpy.Describe(pointFeatures)
                if hasattr(desc, "layer"):
                    overwriteFC = desc.layer.catalogPath
                else:
                    overwriteFC = desc.catalogPath

                arcpy.AddMessage("what is the numberingField: " + numberingField)
                addfield = "Number"
                fnames1 = [field.name for field in arcpy.ListFields(overwriteFC)]
                if addfield in fnames1:
                    arcpy.AddMessage("Number field is already used")
                else:
                    arcpy.AddMessage("Adding Number field to overwriteFC due to no input field")
                    arcpy.AddField_management(overwriteFC,"Number")
                    arcpy.AddMessage("Added Number field to overwriteFC")

                fields = (numberingField, "SHAPE@")

                overwriteCursor = arcpy.da.UpdateCursor(overwriteFC, fields)
                for overwriteRow in overwriteCursor:
                    sortedPointsCursor = arcpy.da.SearchCursor(outputFeatureClass, fields)
                    for sortedRow in sortedPointsCursor:
                        if sortedRow[1].equals(overwriteRow[1]):
                            overwriteRow[0] = sortedRow[0]
                    overwriteCursor.updateRow(overwriteRow)
                arcpy.Delete_management(outputFeatureClass)
                targetLayerName = pointFeatureName
            else:
                targetLayerName = os.path.basename(str(outputFeatureClass))

            #Setting the correct output for the file feature class
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

        return outputFeatureClass
