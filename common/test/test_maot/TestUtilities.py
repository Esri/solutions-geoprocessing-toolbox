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
# TestTemplateConfig.py
# Description: Common objects/methods used by test scripts
# Requirements: ArcGIS Desktop Standard
#------------------------------------------------------------------------------

import arcpy
import os

currentPath = os.path.dirname(__file__)
geodatabasePath = os.path.normpath(os.path.join(currentPath, r"../../../data/geodatabases/"))

scratchPath = geodatabasePath
toolboxesPath = os.path.normpath(os.path.join(currentPath, r"../../../toolboxes/"))                

inputGDB  = os.path.join(geodatabasePath, "test_inputs.gdb")
outputGDB = os.path.join(geodatabasePath, "test_outputs.gdb")
defaultGDB = os.path.join(geodatabasePath, "default.gdb")
scratchGDB = os.path.join(scratchPath, "scratch.gdb")

toolbox = os.path.join(toolboxesPath, "Military Aspects of Terrain Toolbox.tbx")

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
