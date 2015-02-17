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

# GenerateIntermediateLayers

# IMPORTS =======================================================
import os, arcpy, traceback

# ARGUMENTS =====================================================
inputTDSFeatureDataset = arcpy.GetParameterAsText(0)
inputMAOTWorkspace = arcpy.GetParameterAsText(1)

# LOCALS ========================================================
featureClassesToMerge = ["UtilityInfrastructureCrv","StructureCrv","MilitaryCrv","PhysiographyCrv","RecreationCrv","VegetationCrv", "HydrographyCrv","TransportationWaterCrv"]
newList = []
qualifierString = ""
fqClassesToMerge = []
debug = False

# MAIN ==========================================================
try:
    # add qualifier string to FC list name
    arcpy.AddMessage("Getting database qualifier string ...")
    featureDatasetName = os.path.basename(inputTDSFeatureDataset)
    if len(os.path.basename(inputTDSFeatureDataset)) > 4:
       qualifierString = os.path.basename(inputTDSFeatureDataset)[:-4]
    if debug == True: arcpy.AddMessage("qualifier string: " + qualifierString)
    for i in featureClassesToMerge:
       fqClassesToMerge.append(str(qualifierString + i))
    if debug == True: arcpy.AddMessage("fqClassesToMerge: " + str(fqClassesToMerge))

    # get a list of feature classes in the UTDS feature dataset
    workspace = os.path.dirname(inputTDSFeatureDataset)
    arcpy.env.workspace = workspace
    tdsFeatureClasses = arcpy.ListFeatureClasses("*","Line",os.path.basename(inputTDSFeatureDataset))
    if debug == True: arcpy.AddMessage("tdsFeatureClasses: " + str(tdsFeatureClasses))

    # now go through the list of all of them and see which names match our target list, if so, add them to a new list
    arcpy.AddMessage("Building list of input features ...")
    for fc in tdsFeatureClasses:
        if fc in fqClassesToMerge:
            newList.append(str(os.path.join(workspace,featureDatasetName,fc)))
    if debug == True: arcpy.AddMessage("newList: " + str(newList))

    # output feature class name
    target = os.path.join(inputMAOTWorkspace,"HLZCombinedObstacleFeature")
    if debug == True: arcpy.AddMessage("target: " + str(target))

    # merge all FCs into the target FC
    arcpy.AddMessage("Merging features to output (this may take some time)...")
    arcpy.Merge_management(newList,target)
    # set output
    arcpy.AddMessage("Setting output ...")
    arcpy.SetParameter(2,target)

except arcpy.ExecuteError:
    # Get the tool error messages
    msgs = arcpy.GetMessages()
    arcpy.AddError(msgs)
    #print msgs #UPDATE
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
    #print pymsg + "\n" #UPDATE
    print(pymsg + "\n")
    #print msgs #UPDATE
    print(msgs)
