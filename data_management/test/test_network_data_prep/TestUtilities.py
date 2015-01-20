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
# TestUtilities.py
# Description: Common objects/methods used by test scripts
# Requirements: ArcGIS Desktop Advanced
# ----------------------------------------------------------------------------

import arcpy
import os
import sys

# properties: paths
currentPath = os.path.dirname(__file__)
geodatabasePath = os.path.normpath(os.path.join(currentPath, r"../../../data_management/data/geodatabases/"))
scratchPath = geodatabasePath
toolboxesPath = os.path.normpath(os.path.join(currentPath, r"../../../data_management/toolboxes/"))                
# properties: geodatabases
inputGDB  = os.path.join(geodatabasePath, "NetworkPrepData.gdb")
outputGDB = os.path.join(geodatabasePath, "test_outputs.gdb")
# if the output doesn't exist, create it
if not arcpy.Exists(outputGDB): arcpy.CreateFileGDB_management(os.path.dirname(outputGDB),os.path.basename(outputGDB)[:-4])

# properties: toolboxescls
toolbox = os.path.join(toolboxesPath, "Network Data Preparation Tools_10.3.tbx")

def createScratch() :
    try :
        arcpy.CreateFileGDB_management(scratchPath, "scratch")                                          
    except:    
        print "scratch.gdb already exists"
        
    return

def deleteScratch() :
    try :   
        arcpy.Delete_management(scratchGDB)
    except:    
        print "scratch.gdb delete failed"
        
    return    
