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
# ==================================================
# AddUniqueRowID.py
# --------------------------------------------------
# Built for ArcGIS 10.1
# --------------------------------------------------
# Adds a new field of unique row numbers to a table
# ==================================================

# IMPORTS ==========================================
import os, sys, traceback
import arcpy
from arcpy import da

# ARGUMENTS ========================================
dataset = arcpy.GetParameterAsText(0)
fieldName = arcpy.GetParameterAsText(1)

# LOCALS ===========================================
counter = 1

# ==================================================
try:
    
    # add unique ID field
    arcpy.AddMessage("Adding field " + str(fieldName))
    arcpy.AddField_management(dataset,fieldName,"LONG")

    # add unique numbers to each row
    fields = [str(fieldName)]
    arcpy.AddMessage("Adding unique row IDs")
    rows = arcpy.da.UpdateCursor(dataset,fields)
    for row in rows:
        row[0] = counter
        rows.updateRow(row)
        counter += 1
    del rows
    
    # set output
    arcpy.SetParameter(0,dataset)
    

except arcpy.ExecuteError:
    error = True
    # Get the tool error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    #print msgs #UPDATE
    print(msgs)

except:
    # Get the traceback object
    error = True
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