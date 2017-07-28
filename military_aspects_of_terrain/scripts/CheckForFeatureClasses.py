import os, sys, math, traceback
import arcpy

DEBUG = False
deleteme = []
arcpy.env.overwriteOutput = True

if DEBUG == True:
    arcpy.AddMessage("Using scratch GDB of: " + arcpy.env.scratchWorkspace)

# Read in the Parameters
baseFeatureClass = arcpy.GetParameterAsText(0)
obstructionFeatureClasses = arcpy.GetParameterAsText(1)
templateFeatureClass = arcpy.GetParameterAsText(2)
eraseOutputFeatureClass = os.path.join(arcpy.env.scratchWorkspace, "temperase")
unionedFeatureClass = os.path.join(arcpy.env.scratchWorkspace, "tempunion")
splitObstructionFeatureClasses =  obstructionFeatureClasses.split(";")
numFC = len(splitObstructionFeatureClasses)

# Union together the obstructions and then erase them
if obstructionFeatureClasses != "" and numFC > 0:

    arcpy.AddMessage( str(numFC) + " feature class(es) provided")
    # create a value table
    vtab = arcpy.ValueTable(2)
    vtab.loadFromString(obstructionFeatureClasses)

    # union
    arcpy.AddMessage("unionedFeatureClass: " + unionedFeatureClass)
    arcpy.Union_analysis(vtab, unionedFeatureClass)
    deleteme.append(unionedFeatureClass)
    deleteme.append(eraseOutputFeatureClass)
    # Erase
    arcpy.Erase_analysis(baseFeatureClass, unionedFeatureClass, eraseOutputFeatureClass)
    arcpy.CopyFeatures_management(eraseOutputFeatureClass, templateFeatureClass)
    if DEBUG == True:
        arcpy.AddMessage("Features copied from union to template")
else:
    if DEBUG == True:
        arcpy.AddMessage("No obstructions, returning base feature class.")
    arcpy.CopyFeatures_management(baseFeatureClass, templateFeatureClass)
    if DEBUG == True:
        arcpy.AddMessage("Features copied from base to template.")

for i in deleteme:
        if DEBUG == True: 
            arcpy.AddMessage("Removing: " + str(i))
        arcpy.Delete_management(i)
            
arcpy.SetParameter(3,"true")