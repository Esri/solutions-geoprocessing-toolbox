#!/usr/bin/env python
# Import ArcPy site-package and os modules
#
import arcpy 
import os
import sys, traceback
import time
from datetime import datetime
from datetime import date

## ======================================================
## Read in parameters
## ======================================================
featClass = arcpy.GetParameterAsText(0)
    
## ======================================================
## Read geoname file and insert feature
## ======================================================

try:
    messHeader = "==========================================================================="
    messSubHeader = "--------------------------------------------------------"
    
    arcpy.AddMessage(messHeader)
    arcpy.AddMessage(" ")
    arcpy.AddMessage("Checking input feature class " + featClass + "...")
    arcpy.AddMessage(" ")

    hasError = 0
    
    # ======================================================
    # Get shape type and check if point
    # ======================================================
    desc = arcpy.Describe(featClass)

    arcpy.AddMessage(messSubHeader)
    
    arcpy.AddMessage("Geometry Check: Make sure input geometry is point...")
    
    if desc.shapeType.upper() <> "POINT":
        arcpy.AddMessage("-ERROR: Input does not have geometry type of point")
        hasError = hasError + 1
    
    # ======================================================
    # Get list of fields and check if required fields exists
    # ======================================================
    fields = arcpy.ListFields(featClass)
    
    arcpy.AddMessage(messSubHeader)
    
    arcpy.AddMessage("Field Check: Make sure input has correct geonames fields...")

    geonameFields = ["RC", "UFI", "UNI", "LAT", "LONG", "DMS_LAT", "DMS_LONG", "MGRS", "JOG", "FC", \
                  "DSG", "PC", "CC1", "ADM1", "POP", "ELEV", "CC2", "NT", "LC", "SHORT_FORM", \
                  "GENERIC", "SORT_NAME_RO", "FULL_NAME_RO", "FULL_NAME_ND_RO", "SORT_NAME_RG", \
                  "FULL_NAME_RG", "FULL_NAME_ND_RG", "NOTE", "MODIFY_DATE", "COUNTRYCODE1", \
                  "COUNTRYNAME1", "ADM1CODE", "ADM1NAMEALL", "ADM1NAME", "ADM1CLASSALL", \
                  "ADM1CLASS", "PLACENAME", "DSGNAME", "USER_FLD"]
    
    numMissing = 0

    for geonameField in geonameFields:
        found = 0
        for field in fields:
            if geonameField.upper() == field.name.upper():
                found = 1
                break
        if found == 0:
            numMissing = numMissing + 1
            arcpy.AddMessage("- ERROR: Input is missing field: " + geonameField)

    if numMissing > 0:
        hasError = hasError + 1


    # ======================================================
    # Check if input has any features
    # ======================================================
    numCount = long(arcpy.GetCount_management(featClass).getOutput(0))

    arcpy.AddMessage(messSubHeader)
    
    arcpy.AddMessage("Feature Count Check: Make sure input does not have any features...")
    
    if numCount > 0:
        arcpy.AddMessage("- ERROR: Input has " + str(numCount) + " features.")
        hasError = hasError + 1

    # ======================================================
    # Check if input coordinate system is WGS1984
    # ======================================================
    SR = desc.spatialReference

    arcpy.AddMessage(messSubHeader)
    
    arcpy.AddMessage("Spatial Reference Check: Make sure input is 'GCS_WGS_1984'...")

    if SR.name.upper() <> "GCS_WGS_1984":
        arcpy.AddMessage("- ERROR: Spatial Reference is " + SR.name)
        hasError = hasError + 1

    arcpy.AddMessage(" ")
    arcpy.AddMessage(messHeader)


    if hasError > 0:
        result = "FALSE"
    else:
        result = "TRUE"
        
    # Set Output parameter (required so that script 
    # tool output can be connected to other model tools)
    arcpy.SetParameter(1, result)
    
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

