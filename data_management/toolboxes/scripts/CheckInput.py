#!/usr/bin/env python
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
    
    arcpy.AddMessage("Checking input feature class " + featClass + "...")

    hasError = 0
    
    # ======================================================
    # Get shape type and check if point
    # ======================================================
    desc = arcpy.Describe(featClass)
    
    arcpy.AddMessage("Geometry Check: Make sure input feature class geometry is point...")
    
    if desc.shapeType.upper() != "POINT":
        arcpy.AddError("Error: Input feature class does not have geometry type of point")
        hasError = hasError + 1
    
    # ======================================================
    # Get list of fields and check if required fields exists
    # ======================================================
    fields = arcpy.ListFields(featClass)
    
    arcpy.AddMessage("Field Check: Make sure input feature class has correct geonames fields...")

    geonameFields = ["RC", "UFI", "UNI", "LAT", "LONG", "DMS_LAT", "DMS_LONG", "MGRS", "JOG", "FC", \
                  "DSG", "PC", "CC1", "ADM1", "POP", "ELEV", "CC2", "NT", "LC", "SHORT_FORM", \
                  "GENERIC", "SORT_NAME_RO", "FULL_NAME_RO", "FULL_NAME_ND_RO", "SORT_NAME_RG", \
                  "FULL_NAME_RG", "FULL_NAME_ND_RG", "NOTE", "MODIFY_DATE", "COUNTRYCODE1", \
                  "COUNTRYNAME1", "ADM1CODE", "ADM1NAMEALL", "ADM1NAME", "ADM1CLASSALL", \
                  "ADM1CLASS", "PLACENAME", "DSGNAME", "USER_FLD", \
                  "DISPLAY", "NAME_RANK", "NAME_LINK", "TRANSL_CD", "NM_MODIFY_DATE", \
                  "POINT_X", "POINT_Y", "F_EFCTV_DT", "F_TERM_DT"]
    
    numMissing = 0

    for geonameField in geonameFields:
        found = 0
        for field in fields:
            if geonameField.upper() == field.name.upper():
                found = 1
                break
        if found == 0:
            numMissing = numMissing + 1
            arcpy.AddError("Error: Input feature class is missing field: " + geonameField)

    if numMissing > 0:
        hasError = hasError + 1


    # ======================================================
    # Check if input has any features
    # ======================================================
    if sys.version_info[0] > 2:
        numCount = int(arcpy.GetCount_management(featClass).getOutput(0))
    else:
        numCount = long(arcpy.GetCount_management(featClass).getOutput(0))
    
    arcpy.AddMessage("Feature Count Check: Make sure input feature class does not have any features...")
    
    if numCount > 0:
        arcpy.AddError("Error: Input feature class has " + str(numCount) + " features.")
        hasError = hasError + 1

    # ======================================================
    # Check if input coordinate system is WGS1984
    # ======================================================
    SR = desc.spatialReference
    
    arcpy.AddMessage("Spatial Reference Check: Make sure input feature class is 'GCS_WGS_1984'...")

    if SR.name.upper() != "GCS_WGS_1984":
        arcpy.AddError("Error: Spatial Reference is " + SR.name)
        hasError = hasError + 1

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

