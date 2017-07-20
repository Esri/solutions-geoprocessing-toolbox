
# Esri start of added imports
import sys, os, arcpy
# Esri end of added imports

# Esri start of added variables
g_ESRI_variable_1 = 'TEXT'
g_ESRI_variable_2 = 'NEW_SELECTION'
g_ESRI_variable_3 = 'PYTHON_9.3'
# Esri end of added variables

import arcpy, os

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "RangeDomePyTools"
        self.alias = "RangeDomePyTools"
        self.helpContext = 50

        # List of tool classes associated with this toolbox
        self.tools = [ShowNonClosedVolumes]


class ShowNonClosedVolumes(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Detect non-closed volumes"
        self.description = "This tool finds all non-closed volumes input features class" +\
                            "and displays them in 1 feature class"
        self.canRunInBackground = False
        self.helpContext = 50000001

    def getParameterInfo(self):
        """Define parameter definitions"""
        inputFC = arcpy.Parameter(displayName="Input Features",
                                  name="input_fc",
                                  datatype="GPFeatureLayer",
                                  parameterType="Required",
                                  direction="Input")

        outputFC = arcpy.Parameter(displayName="Output Features",
                                  name="output_fc",
                                  datatype="DEFeatureClass",
                                  parameterType="Required",
                                  direction="Output")

        parameters = [inputFC,outputFC]
        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def getWorkSpaceFromFeatureClass(self, feature_class):
        dirname = os.path.dirname(arcpy.Describe(feature_class).catalogPath)
        desc = arcpy.Describe(dirname)

        if hasattr(desc, "datasetType") and desc.datasetType=='FeatureDataset':
            dirname = os.path.dirname(dirname)

        return dirname

    def delete_featureclasses(self, feature_classes):
        for fc in feature_classes:
            if arcpy.Exists(fc):
                arcpy.Delete_management(fc)

    def execute(self, parameters, messages):
        """The source code of the tool."""

        class GenericError(Exception):
            def __init__(self, value):
                self.value = value
            def __str__(self):
                return repr(self.value)

        try:
            # Toolbox variables
#           for debug only, disable for running in ArcGIS!
#           debug variables
#            input_fc = r"D:/Gert/Work/Esri/Solutions/Defense/Work/Pro/RangeDomeAnalysis2.0.0/Maps_and_GDBs/Intermediate.gdb/QA_MaxZone_CE_enclosed"
#            output_fc = r"D:/Gert/Work/Esri/Solutions/Defense/Work/Pro/RangeDomeAnalysis2.0.0/Maps_and_GDBs/Intermediate.gdb/FlightCorridor_Lethal_error"

#            # Toolbox variables
            input_fc = parameters[0].valueAsText
            output_fc = parameters[1].valueAsText

            input_fc_lyr = "input_fc_lyr"
            warning_field = "Warning"
            fieldList = ["IsClosed"]
            errorList = [0]

            workspace = self.getWorkSpaceFromFeatureClass(input_fc)
            length = len(workspace)

            if length > 0:
                arcpy.env.workspace = workspace
                arcpy.env.overwriteOutput = True
               # check IsClosed field and values
                if arcpy.ListFields(input_fc, fieldList):
                    with arcpy.da.SearchCursor(input_fc, fieldList[0]) as cursor:
                        for row in cursor:
                            if row[0] == None or row[0] == ' ':
                                errorList[0] = 1

                    if  errorList[0]  == 1 :
                        raise GenericError("One or more fields has empty or NULL values.")
                    else :

                        # add warning text field
                        arcpy.AddField_management(input_fc, warning_field, g_ESRI_variable_1)

                        #select non-closed volumes and write to output feature class
                        # feature layers for selection
                        arcpy.MakeFeatureLayer_management(input_fc,input_fc_lyr)
                        expression1 = fieldList[0] + " = 'No'"
                        arcpy.SelectLayerByAttribute_management(input_fc_lyr,g_ESRI_variable_2, expression1)
                        expression = "'Threat detection error: assume threat to ground level'"
                        arcpy.CalculateField_management(input_fc_lyr, warning_field, expression, g_ESRI_variable_3)
                        arcpy.CopyFeatures_management(input_fc_lyr, output_fc)

                else :
                    raise GenericError("IsClosed field does NOT exist.")

            else:
                raise GenericError("Invalid workspace")

        except GenericError as e:
            arcpy.AddError("Generic error: "+e.value)
            print(("Generic error: "+e.value))
            print((arcpy.GetMessages(2)))

        except arcpy.ExecuteError:
            print((arcpy.GetMessages(2)))

        except arcpy.ExecuteWarning:
            print((arcpy.GetMessages(1)))
        return

# for debug only!
#def main():
#    tbx = Toolbox()
#    tool = ShowNonClosedVolumes()
#    tool.execute(tool.getParameterInfo(),None)

#if __name__ == "__main__":
#    main()
