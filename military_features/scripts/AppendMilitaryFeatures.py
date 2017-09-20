#----------------------------------------------------------------------------------
# Copyright 2013 Esri
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
#----------------------------------------------------------------------------------
# AppendMilitaryFeatures.py
# Description: This PY file handles the GP input, validation, and output for
#              the Append Military Features command line tool 
# Requirements: ArcGIS Desktop Advanced (Advanced needed to change Representation Rules)
#----------------------------------------------------------------------------------

# IMPORTS ==========================================
import os
import sys
import traceback
import subprocess
import arcpy

try:
    
    # SCRIPT ARGUMENTS =================================
    inputTable = arcpy.GetParameterAsText(0)
    targetGeodatabase = arcpy.GetParameterAsText(1)
    sidcField = arcpy.GetParameterAsText(2)
    standard = arcpy.GetParameterAsText(3)
    
    # CONSTANTS ========================================
    
    # LOCALS ===========================================
    debug = True # switch off if detailed info not needed
    
    # LICENSE ==========================================
        
    # Check that we have Advanced/ArcInfo
    licenseState = arcpy.CheckProduct("ArcInfo")
    arcpy.AddMessage("ArcGIS Advanced/ArcInfo license state = " + licenseState)
    if (licenseState == "Unavailable") or (licenseState == "NotLicensed") :
        arcpy.AddError("Editing Representation Rules requires Desktop Advanced License (ArcInfo) - Tool can't continue")    
        raise Exception('License Error')
            
    # MAIN ============================================    
            
    # set command line arguments - Note: need quotes("") around command line arguments (to handle spaces)
    arguments = "\"" + str(inputTable) + "\" " + "\"" + str(targetGeodatabase) \
        + "\" " + str(sidcField) + " " + str(standard)
    
    # set command string
    # AppendMilitaryFeatures.exe <inputFeatureClass> <outputGDB> [sicField]
    currentPath = os.path.dirname(__file__)
    EXE_PATH = os.path.normpath(os.path.join(currentPath, r"../../application/"))
    if not os.path.exists(EXE_PATH):
        EXE_PATH = os.path.normpath(os.path.join(currentPath, r"../application/"))
    if not os.path.exists(EXE_PATH):
        arcpy.AddError("Could not find AppendMilitaryFeatures.exe at: " + str(EXE_PATH))
        raise Exception("Could not find required path") 

    EXE_PATH_AND_FILE = "\"" + os.path.join(EXE_PATH, r"AppendMilitaryFeatures.exe") + "\""
    EXE_CMD = EXE_PATH_AND_FILE + r" " + arguments
    LOG_FILENAME = os.path.normpath(os.path.join(EXE_PATH, r"log.txt"))
    COMMAND_LINE = EXE_CMD + r" > " + "\"" + LOG_FILENAME + "\""
    # Ex: COMMAND_LINE=r"AppendMilitaryFeatures.exe arg1 arg2 arg3 > c:/temp/log.txt"
    
    # Run the command at a command prompt
    if debug == True: arcpy.AddMessage("Command string: \n" + str(COMMAND_LINE))

    # Popen Version with Return Code:
    proc = subprocess.Popen(COMMAND_LINE, shell=True) 
    proc.wait()
    retCode = proc.returncode

    # Send entire console log file to ArcPy Messages (so we know what happened):
    logFile = open(LOG_FILENAME, "r") 
    for line in logFile: 
        nonewline = line.strip('\n')
        arcpy.AddMessage(nonewline) 

    osmsg = "Return Code: " + str(retCode)
    arcpy.AddMessage(osmsg)

    if (retCode > 0) and (retCode < 8) :
        errorDictionary = {}
        errorDictionary[0] = 'No Error'
        errorDictionary[1] = 'Failed to load dependent data files'
        errorDictionary[2] = 'Input Dataset does not exist/can not be opened'
        errorDictionary[3] = 'No military features found in input'
        errorDictionary[4] = 'Output GDB does not exist/can not be opened'
        errorDictionary[5] = 'Exclusive Schema Lock could not be obtained on Output GDB'
        errorDictionary[6] = 'No [SIDC] field in input data'
        errorDictionary[7] = 'Could not find required Style Files - check ArcGIS Styles folder'

        arcpy.AddError(errorDictionary[retCode])
    
    # Set output
    arcpy.SetParameter(4, targetGeodatabase)

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

finally:
    # cleanup (if there is anything to clean up)
    if debug == True: arcpy.AddMessage("Done")
