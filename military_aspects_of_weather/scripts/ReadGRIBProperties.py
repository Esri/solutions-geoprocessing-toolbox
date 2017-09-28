#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------
# ReadGRIBProperties.py
# Description: Read GRIB Properties - Reports the metadata for GRIB files in a
#              folder to an output text file
# Requirements: ArcGIS Desktop Basic, DeGRIB executable (3rd party)
# -----------------------------------------------------------------------------
# History:
# 3/27/2015 - mf - Checked for Python 3 compatibility - No changes needed


import arcpy
import os
import subprocess

# Grab the input folder and make a reference to all files within it (using the * wildcard)
inputfolder = arcpy.GetParameterAsText(0)
if (not os.path.exists(inputfolder)):
    arcpy.AddError("The folder '" + inputfolder + "' does not exist.")
    sys.exit()

inputfolder = os.path.normpath(inputfolder) + "\\*"

# Get the pathname to this script
scriptPath = sys.path[0]

# Get the pathnames to relevant folders
toolboxesPath = os.path.dirname(scriptPath)
templatePath = os.path.dirname(toolboxesPath)
appPath = os.path.join(templatePath, "application")

#Get the path to the Degrib executable (NB: This path must NOT contain spaces)
#ANT should have built the executable into your template...
degribExec = os.path.join(appPath, r"degrib\bin\degrib.exe")

if not os.path.exists(degribExec):
   arcpy.AddError("The specified path to DeGRIB does not exist - '" + degribExec + "'")
   sys.exit()
elif degribExec.find(" ") >= 0:
   arcpy.AddError("The path to the DeGRIB executable must not contain any spaces")
   sys.exit()
   
# Define a text file in the scratch folder for writing the output to
outfile = os.path.join(arcpy.env.scratchFolder, "InspectGRIBFolderOutput.csv")

cmdLine = degribExec + " \"" + inputfolder + "\" -I > \"" + outfile + "\""
arcpy.AddMessage("\n" + cmdLine + "\n")

os.system(cmdLine)

# Write the output to the message window
if os.path.exists(outfile):
    f = open(outfile, "r")
    arcpy.AddMessage(f.read())
    f.close()
    arcpy.AddMessage("\nOutput has been written to " + outfile + "\n\n")
else:
    file = ""
    arcpy.AddMessage("No output has been created. Check that the specified folder contains GRIB files.")
    
arcpy.SetParameterAsText(1, outfile)