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
# ReadNetCDFProperties.py
# Description: Read NetCDF Properties - Reports the metadata for a NetCDF file
#              to an output text file
# Requirements: ArcGIS Desktop Basic
# ----------------------------------------------------------------------------
# History:
# 3/27/2015 - mf - Checked for Python 3 compatibility - No changes needed.
#

import arcpy
import os

InNetCDF = arcpy.GetParameterAsText(0)

# Get the pathname to this script
scriptPath = sys.path[0]

#Define a text file in the scratch folder for writing the output to
outfile = os.path.join(arcpy.env.scratchFolder, "InspectNetCDFFileOutput.txt")
#Open the outfile
file = open(outfile, "w")

ncFP = arcpy.NetCDFFileProperties(InNetCDF)

#Get Variables
arcpy.AddMessage("\n\n*** Variables ***")
file.write("*** Variables ***")
ncVars = ncFP.getVariables()
for ncVar in ncVars:
    arcpy.AddMessage("\nVariable: %s" % ncVar)
    file.write("\n\nVariable: %s" % ncVar)
    ncVarType = ncFP.getFieldType(ncVar)        
    arcpy.AddMessage("\t" + "Variable type: %s " % ncVarType)
    file.write("\n\t" + "Variable type: %s " % ncVarType)

    #Get dimensions by variable        
    ncDimsByVar = ncFP.getDimensionsByVariable(ncVar)
    dims = "\t" + "Dimensions:"
    for ncDimByVar in ncDimsByVar:
        dims += " " + ncDimByVar
    arcpy.AddMessage(dims)
    file.write("\n" + dims)

    #Get Variable Attribues
    ncVANames = ncFP.getAttributeNames(ncVar)

    for ncVAName in ncVANames:
        arcpy.AddMessage("\t%s = %s" % (ncVAName, ncFP.getAttributeValue(ncVar, ncVAName)))        
        file.write("\n\t%s = %s" % (ncVAName, ncFP.getAttributeValue(ncVar, ncVAName)))        

#Get Global Attribues
arcpy.AddMessage("\n\n*** Global Attributes ***\n")
file.write("\n\n\n*** Global Attributes ***\n")
ncAttributeNames = ncFP.getAttributeNames("")
for ncAttributeName in ncAttributeNames:
    arcpy.AddMessage("%s = %s\n" % (ncAttributeName, ncFP.getAttributeValue("", ncAttributeName)))
    file.write("\n%s = %s\n" % (ncAttributeName, ncFP.getAttributeValue("", ncAttributeName)))

file.close()

arcpy.AddMessage("\nOutput has been written to " + file.name + "\n\n")

arcpy.SetParameterAsText(1, file.name)