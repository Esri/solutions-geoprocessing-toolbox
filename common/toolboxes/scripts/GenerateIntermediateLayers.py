
# GenerateIntermediateLayers

# IMPORTS =======================================================
import os, arcpy, traceback

# ARGUMENTS =====================================================
inputUTDSFeatureDataset = arcpy.GetParameterAsText(0)
inputMAOTWorkspace = arcpy.GetParameterAsText(1)

# LOCALS ========================================================
featureClassesToMerge = ["AgricultureSrf","SettlementSrf","CultureSrf","PhysiographySrf","RecreationSrf","VegetationSrf"]
newList = []
qualifierString = ""
fqClassesToMerge = []
debug = True

# MAIN ==========================================================
try:
    # add qualifier string to FC list name
    arcpy.AddMessage("Getting database qualifier string ...")
    featureDatasetName = os.path.basename(inputUTDSFeatureDataset)
    if len(os.path.basename(inputUTDSFeatureDataset)) > 4:
       qualifierString = os.path.basename(inputUTDSFeatureDataset)[:-4]
    if debug == True: arcpy.AddMessage("qualifier string: " + qualifierString)
    for i in featureClassesToMerge:
       fqClassesToMerge.append(str(qualifierString + i))
    if debug == True: arcpy.AddMessage("fqClassesToMerge: " + str(fqClassesToMerge))
    
    # get a list of feature classes in the UTDS feature dataset
    workspace = os.path.dirname(inputUTDSFeatureDataset)
    arcpy.env.workspace = workspace
    utdsFeatureClasses = arcpy.ListFeatureClasses("*","Polygon",os.path.basename(inputUTDSFeatureDataset))
    if debug == True: arcpy.AddMessage("utdsFeatureClasses: " + str(utdsFeatureClasses))
    
    # now go through the list of all of them and see which names match our target list, if so, add them to a new list
    arcpy.AddMessage("Building list of input features ...")
    for fc in utdsFeatureClasses:
        if fc in fqClassesToMerge:
            newList.append(str(os.path.join(workspace,featureDatasetName,fc)))
    if debug == True: arcpy.AddMessage("newList: " + str(newList))

    # output feature class name
    target = os.path.join(inputMAOTWorkspace,"CombinedVegetationCoverage")
    if debug == True: arcpy.AddMessage("target: " + str(target))
    
    # merge all FCs into the target FC
    arcpy.AddMessage("Merging features to output (this may take some time)...")
    arcpy.Merge_management(newList,target)
    
    # set output
    if debug == True: arcpy.AddMessage("Setting output ...")
    arcpy.SetParameter(2,target)
    
except arcpy.ExecuteError: 
    # Get the tool error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    print msgs

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
    print pymsg + "\n"
    print msgs