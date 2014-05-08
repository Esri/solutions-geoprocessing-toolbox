import os, sys, math, traceback
import arcpy

arcpy.AddMessage("Using scratch GDB of: " + arcpy.env.scratchGDB)

# Read in the Parameters
baseFeatureClass = arcpy.GetParameterAsText(0)
obstructionFeatureClasses = arcpy.GetParameterAsText(1)
templateFeatureClass = arcpy.GetParameterAsText(2)
eraseOutputFeatureClass = arcpy.env.scratchGDB + "\\temperase"
unionedFeatureClass = arcpy.env.scratchGDB + "\\tempunion"
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
	
	# Erase
	arcpy.Erase_analysis(baseFeatureClass, unionedFeatureClass, eraseOutputFeatureClass)
	arcpy.CopyFeatures_management(eraseOutputFeatureClass, templateFeatureClass)
	arcpy.AddMessage("Features copied from union to template")
else:
	arcpy.AddMessage("No obstructions, returning base feature class.")
	arcpy.CopyFeatures_management(baseFeatureClass, templateFeatureClass)
	arcpy.AddMessage("Features copied from base to template.")

arcpy.SetParameter(3,"true")