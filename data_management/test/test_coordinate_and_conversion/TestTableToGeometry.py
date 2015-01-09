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
# Name: TableToGeometry.py
# Description: Automatic Test of Range Rings Model
# Requirements: ArcGIS Desktop Standard
#------------------------------------------------------------------------------

import arcpy
import os
import sys
import traceback

import TestUtilities

def RunTestTableToPoints():
    
    arcpy.AddMessage("Starting Test: TableToPoint")
                
    inputTable =  os.path.join(TestUtilities.csvPath, "pointwizard.csv")
    outputPointsFC =  os.path.join(TestUtilities.outputGDB, "TableToPoint")
        
    inputFeatureCount = int(arcpy.GetCount_management(inputTable).getOutput(0)) 
    print("Input FeatureClass: " + str(inputTable))
    print("Input Feature Count: " +  str(inputFeatureCount))
        
    if (inputFeatureCount < 1) :
        print("Invalid Input Feature Count: " +  str(inputFeatureCount))
                   
    coordinateConversionFormat = 'MGRS'
    coordinateFieldX = 'MGRS'
    coordinateFieldY = 'MGRS'
    
    ########################################################3
    # Execute the Model under test:   
    
    # sample params:
    # '\csv\ConversionPoints.csv', 'MGRS', 'MGRS', 'MGRS', 'geodatabases\test_outputs.gdb\TableToPoint'
    
    arcpy.TableToPoint_CnC(inputTable, coordinateConversionFormat, coordinateFieldX, coordinateFieldY, outputPointsFC)
    ########################################################3

    # Verify the results    
    outputFeatureCount = int(arcpy.GetCount_management(outputPointsFC).getOutput(0)) 
    print("Output FeatureClass: " + str(outputPointsFC))
    print("Output Feature Count: " +  str(outputFeatureCount))
                
    if (outputFeatureCount <>  inputFeatureCount) :
        print("Input / Output Feature Count don't match: " +  str(inputFeatureCount) + ":" + str(outputFeatureCount))
        raise Exception("Test Failed")                        
    
    print("Test Successful")
    
def RunTestTableToPolyline():
    
    arcpy.AddMessage("Starting Test: TableToPolyline")
                
    inputTable =  os.path.join(TestUtilities.csvPath, "linewizard.csv")
    outputLinesFC =  os.path.join(TestUtilities.outputGDB, "TableToLine")
        
    inputFeatureCount = int(arcpy.GetCount_management(inputTable).getOutput(0)) 
    print("Input FeatureClass: " + str(inputTable))
    print("Input Feature Count: " +  str(inputFeatureCount))
        
    if (inputFeatureCount < 1) :
        print("Invalid Input Feature Count: " +  str(inputFeatureCount))
                   
    coordinateConversionFormat = 'DD_2'
    coordinateFieldX = 'Lond'
    coordinateFieldY = 'Latd'
    lineJoinIdField = 'Id'
    
    ########################################################3
    # Execute the Model under test:   
    
    # sample params:
    # 'data\csv\linewizard.csv', 'DD_2', 'Lond', 'Latd', 
    # 'data\geodatabases\test_outputs.gdb\TableToMultipoint', 'Id', "#', "#'
            
    arcpy.TableToPolyline_CnC(inputTable, coordinateConversionFormat, coordinateFieldX, coordinateFieldY, outputLinesFC, lineJoinIdField)
    ########################################################3

    # Verify the results    
    outputFeatureCount = int(arcpy.GetCount_management(outputLinesFC).getOutput(0)) 
    print("Output FeatureClass: " + str(outputLinesFC))
    print("Output Feature Count: " +  str(outputFeatureCount))
                
    if (outputFeatureCount < 1) :
        print("Input / Output Feature Count < 1: " +  str(outputFeatureCount))
        raise Exception("Test Failed")                        
    
    print("Test Successful")
    
def RunTestTableToEllipse():
    
    arcpy.AddMessage("Starting Test: TableToEllipse")
                
    inputTable =  os.path.join(TestUtilities.csvPath, "ellipsewizard.csv")
    outputEllipsesFC =  os.path.join(TestUtilities.outputGDB, "TableToEllipse")
        
    inputFeatureCount = int(arcpy.GetCount_management(inputTable).getOutput(0)) 
    print("Input FeatureClass: " + str(inputTable))
    print("Input Feature Count: " +  str(inputFeatureCount))
        
    if (inputFeatureCount < 1) :
        print("Invalid Input Feature Count: " +  str(inputFeatureCount))
                   
    coordinateConversionFormat = 'DD_2'
    coordinateFieldX = 'Lond'
    coordinateFieldY = 'Latd'
    majorAxisField = 'Major'
    minorAxisField = 'Minor'
    axisUnit = 'KILOMETERS'
    orientationField = 'Orient'
    orientationUnit = 'DEGREES'
    sr = '#'     
    
    ########################################################3
    # Execute the Model under test:   
    
    # sample params:
    # 'data\csv\ellipsewizard.csv', 'DD_2', 'Lond', 'Latd', 'Major', 'Minor', 'KILOMETERS', 'Orient', 'DEGREES'
    # '#', 'geodatabases\test_outputs.gdb\TableToEllipse'
    arcpy.TableToEllipse_CnC(inputTable, coordinateConversionFormat, coordinateFieldX, coordinateFieldY, majorAxisField,
                                  minorAxisField, axisUnit, outputEllipsesFC, orientationField, orientationUnit, sr)
    ########################################################3

    # Verify the results    
    outputFeatureCount = int(arcpy.GetCount_management(outputEllipsesFC).getOutput(0)) 
    print("Output FeatureClass: " + str(outputEllipsesFC))
    print("Output Feature Count: " +  str(outputFeatureCount))
                
    if (outputFeatureCount <>  inputFeatureCount) :
        print("Input / Output Feature Count don't match: " +  str(inputFeatureCount) + ":" + str(outputFeatureCount))
        raise Exception("Test Failed")                              
    
    print("Test Successful")
    
def RunTestTableToLOB():
    
    arcpy.AddMessage("Starting Test: TableToLOB")
                
    inputTable =  os.path.join(TestUtilities.csvPath, "lobwizard.csv")
    outputLinesFC =  os.path.join(TestUtilities.outputGDB, "TableToLOB")
        
    inputFeatureCount = int(arcpy.GetCount_management(inputTable).getOutput(0)) 
    print("Input FeatureClass: " + str(inputTable))
    print("Input Feature Count: " +  str(inputFeatureCount))
        
    if (inputFeatureCount < 1) :
        print("Invalid Input Feature Count: " +  str(inputFeatureCount))
                   
    coordinateConversionFormat = 'DD_2'
    coordinateFieldX = 'Lond'
    coordinateFieldY = 'Latd'
    bearingUnit = 'DEGREES'
    bearingField = 'Azimuth' 
    distanceUnit = 'METERS'
    distanceField = 'Distance'
    lineType = 'GEODESIC'    
    
    ########################################################3
    # Execute the Model under test:   
    
    # sample params:
    # 'data\csv\lobwizard.csv', 'DD_2', 'Lond', 'Latd', 'DEGREES', 'Azimuth', 'METERS', 
    # 'Distance', 'GEODESIC', 'data\geodatabases\test_outputs\TableToLOB'    
            
    arcpy.TableToLOB_CnC(inputTable, coordinateConversionFormat, coordinateFieldX,  coordinateFieldY, bearingUnit,
                              bearingField, distanceUnit, distanceField, outputLinesFC, lineType)
    ########################################################3

    # Verify the results    
    outputFeatureCount = int(arcpy.GetCount_management(outputLinesFC).getOutput(0)) 
    print("Output FeatureClass: " + str(outputLinesFC))
    print("Output Feature Count: " +  str(outputFeatureCount))
                
    if (outputFeatureCount <>  inputFeatureCount) :
        print("Input / Output Feature Count don't match: " +  str(inputFeatureCount) + ":" + str(outputFeatureCount))
        raise Exception("Test Failed")                        
    
    print("Test Successful")
  
try:
        
    print("Running from: " + str(TestUtilities.currentPath))
    print("Geodatabase path: " + str(TestUtilities.geodatabasePath))
    
    print("Creating New Scratch Workspace")
    TestUtilities.createScratch()

    toolbox = TestUtilities.toolbox        
            
    arcpy.env.overwriteOutput = True
    arcpy.env.scratchWorkspace = TestUtilities.scratchGDB
    arcpy.ImportToolbox(toolbox, "CnC")

    ################################################
    # Run Individual Geometry Importer Tests
    print("Testing all TableTo{Geometry} Models...")
    
    RunTestTableToPoints()
    RunTestTableToPolyline()
    RunTestTableToEllipse()
    RunTestTableToLOB()
   
    
    ################################################
    
    print("Deleting Scratch Workspace")
    TestUtilities.deleteScratch()        
                
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
    arcpy.AddError(msgs)

    # return a system error code
    sys.exit(-1)

