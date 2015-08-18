# -*- coding: utf-8 -*-
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

# ==================================================
# ImportPatrolReport.py
# --------------------------------------------------
# requirments: ArcGIS 10.3, Python 2.7 or Python 3.4
# author: ArcGIS Solutions
# company: Esri
# ==================================================
# description: <Description>
# ==================================================
# history:
# 8/14/2015 - mf - Built script tool from original model
# ==================================================

# Import arcpy module
import arcpy
import os
import sys
import traceback

# Script arguments
inputTrackLines = arcpy.GetParameterAsText(0)
inputTrackIDFieldName = arcpy.GetParameterAsText(1)
inputPatrolReportXML = arcpy.GetParameterAsText(2)
inputPatrolReportTable = arcpy.GetParameterAsText(3)
inputEnemySightingsTable = arcpy.GetParameterAsText(4)

DEBUG = False

def getUniqueID(featlayer, idfield):
    uniqueid, rows, row = None, None, None
    try:
        count = int(arcpy.GetCount_management(featlayer).getOutput(0))
        rows = arcpy.da.SearchCursor(featlayer,["OID@",idfield])
        row = rows.next() #get the first row only
        uniqueid = row[1]
        oid = row[0]
        if count > 1:
            arcpy.AddWarning("Found more than one selected row. Using row with Object ID = " + str(oid) + ", and with value: " + str(uniqueid))
        del row
        del rows
        return uniqueid

    except Exception as e:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"
        # Return python error messages for use in script tool or Python Window
        arcpy.AddError(pymsg)
        print(pymsg)
        arcpy.AddError(msgs)
        print(msgs)


def getToolboxName():
    versionDesktop = ["10.1.0","10.2.0","10.2.1","10.2.2","10.3.0","10.3.1","10.4.0"]
    versionPro = ["1.0","1.1"]
    version = arcpy.GetInstallInfo()["Version"]
    if version in versionDesktop:
        tbxName = "Patrol Data Capture Tools_10.3.tbx"
        
    elif version in versionPro:
        tbxName = "Patrol Data Capture Tools.tbx"
    else:
        raise Exception("Unable to determine ArcGIS version")
    if DEBUG == True:
        arcpy.AddMessage("Version " + str(version) + " using " + tbxName)
    return tbxName

def getToolboxPath():
    tbxPath = os.path.dirname(os.path.dirname(sys.argv[0]))
    #tbxPath = r"C:/Users/matt2542/Documents/GitHub/solutions-geoprocessing-toolbox/data_management/toolboxes"
    if DEBUG == True:
        arcpy.AddMessage("Using toolbox path: " + str(tbxPath))
    return tbxPath

def main():
    try:
        tbx = os.path.join(getToolboxPath(),getToolboxName())
        if not (os.path.exists(tbx)):
            raise Exception("Cannot find toolbox: " + str(tbx))

        # Load required toolboxes
        arcpy.ImportToolbox(tbx,"pdc")

        # Set Geoprocessing environments
        arcpy.env.overwriteOutput = True

        # Process: Calculate Value
        uniqueID = getUniqueID(inputTrackLines, inputTrackIDFieldName)
        arcpy.AddMessage("Using unique ID = " + str(uniqueID))

        # Process: Import Enemy Sightings
        arcpy.AddMessage("Adding Enemy Sightnings...")
        arcpy.ImportEnemySightingsXML_pdc(inputPatrolReportXML, uniqueID, inputEnemySightingsTable)

        # Process: Import Patrol Rpt XML
        arcpy.AddMessage("Adding Patrol Report...")
        arcpy.ImportPatrolRptXML_pdc(inputPatrolReportXML, uniqueID, inputPatrolReportTable)

        arcpy.AddMessage("Done!")
        arcpy.SetParameter(5,inputEnemySightingsTable)
        arcpy.SetParameter(6,inputPatrolReportTable)

    except arcpy.ExecuteError:
        # Get the tool error messages
        msgs = arcpy.GetMessages()
        arcpy.AddError(msgs)

        # return a system error code
        sys.exit(-1)

    except Exception as e:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]

        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

        # Return python error messages for use in script tool or Python Window
        arcpy.AddError(pymsg)
        print(pymsg)
        arcpy.AddError(msgs)
        print(msgs)

# MAIN =============================================
if __name__ == "__main__":
    main()
    