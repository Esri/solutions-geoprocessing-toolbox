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

import os
import logging
import arcpy
import unittest
import Configuration
import UnitTestUtilities

class FindLocalPeaksTestCase(unittest.TestCase):
    
    visGDB = os.path.join(Configuration.vis_GeodatabasePath, "test_vis_and_range_inputs.gdb")
    inputPolygonFC = os.path.join(visGDB, "samplePolygonArea")
    inputSurface = os.path.join(visGDB, "Jbad_SRTM_USGS_EROS")
    outputPointsFC = os.path.join(Configuration.vis_ScratchPath, "LocalPeaks")
    
    def setUp(self):
        UnitTestCase.UnitTestCase.setUp(self)
        testObjects = [Configuration.visandRangeToolbox, self.visGDB, self.inputPolygonFC, self.inputSurface]
        UnitTestUtilities.checkGeoObjects(testObjects)
        UnitTestUtilities.createScratch(Configuration.vis_ScratchPath)
        
    def test_local_peaks(self):
        try:
            arcpy.AddMessage("Testing Find Local Peaks (unit).")
            if arcpy.CheckExtension("Spatial") == "Available":
                arcpy.CheckOutExtension("Spatial")
            else:
                raise Exception("LicenseError")
                
            print("Importing Visibility and Range Toolbox...")
            arcpy.ImportToolbox(Configuration.visandRangeToolbox, "VandR")
            arcpy.env.overwriteOutput = True

            inputFeatureCount = int(arcpy.GetCount_management(self.inputPolygonFC).getOutput(0)) 
            print("Input FeatureClass: " + str(self.inputPolygonFC))
            print("Input Feature Count: " +  str(inputFeatureCount))
            
            self.assertTrue(inputFeatureCount > 0)
            
            # if (inputFeatureCount < 1):
                # print("Invalid Input Feature Count: " +  str(inputFeatureCount))
           
            numberOfPeaks = 3
           
            ########################################################
            # Execute the Model under test:   
            arcpy.FindLocalPeaks_VandR(self.inputPolygonFC, numberOfPeaks, self.inputSurface, self.outputPointsFC)
            ########################################################
    
            # Verify the results    
            outputFeatureCount = int(arcpy.GetCount_management(self.outputPointsFC).getOutput(0)) 
            print("Output FeatureClass: " + str(self.outputPointsFC))
            print("Output Feature Count: " +  str(outputFeatureCount))
            self.assertEqual(outputFeatureCount, 3)       
            
            # if (outputPointsFC < 3):
                # print("Invalid Output Feature Count: " +  str(outputFeatureCount))
                # raise Exception("Test Failed")
                
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
            
        except:
            UnitTestUtilities.handleGeneralError()
        
        finally:
            arcpy.CheckInExtension("Spatial")