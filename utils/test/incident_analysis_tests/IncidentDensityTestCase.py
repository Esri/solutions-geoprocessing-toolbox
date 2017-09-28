# coding: utf-8
'''
-----------------------------------------------------------------------------
Copyright 2016 Esri
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-----------------------------------------------------------------------------

==================================================
IncidentDensityTestCase.py
--------------------------------------------------
requirments: ArcGIS X.X, Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
history:
12/16/2015 - JH - initial creation
09/20/2016 - MF - Update to two method test pattern 
07/28/2017 - CM - Refactor
==================================================
'''

import unittest
import arcpy
import os

# Add parent folder to python path if running test case standalone
import sys
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import UnitTestUtilities
import Configuration
import DataDownload

class IncidentDensityTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Incident Density tool
    in the Incident Analysis toolbox'''
  
    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime
    toolboxUnderTestAlias = 'iaTools'
       
    incidentScratchGDB = None

    inputPointFeatures = None
    inputBoundaryFeatures = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print(".....IncidentDensityTestCase.setUp")    

        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''

        self.toolboxUnderTest = Configuration.incidentToolboxPath + Configuration.GetToolboxSuffix()

        UnitTestUtilities.checkArcPy()
        
        DataDownload.runDataDownload(Configuration.incidentAnalysisDataPath, Configuration.incidentInputGDB, Configuration.incidentURL)
      
        if (self.incidentScratchGDB == None) or (not arcpy.Exists(self.incidentScratchGDB)):
            self.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentAnalysisDataPath)
         
        self.inputPointFeatures = os.path.join(Configuration.incidentInputGDB, "Incidents")
        self.inputBoundaryFeatures = os.path.join(Configuration.incidentInputGDB, "Districts")

        UnitTestUtilities.checkFilePaths([Configuration.incidentAnalysisDataPath])

        UnitTestUtilities.checkGeoObjects([Configuration.incidentInputGDB, \
                                           Configuration.incidentResultGDB, \
                                           self.toolboxUnderTest, \
                                           self.inputPointFeatures, \
                                           self.inputBoundaryFeatures])

    def tearDown(self):
        if Configuration.DEBUG == True: print(".....IncidentDensityTestCase.tearDown")
        UnitTestUtilities.deleteScratch(self.incidentScratchGDB)
        
    def test_incident_density(self):
        '''test_incident_density'''
        if Configuration.DEBUG == True: print(".....IncidentDensityTestCase.test_incident_density")
           
        arcpy.ImportToolbox(self.toolboxUnderTest, self.toolboxUnderTestAlias)

        runToolMsg = "Running tool (Incident Density)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)

        outputDensity = os.path.join(Configuration.incidentResultGDB, "outputDensity")

        # Delete the feature class used to load if already exists
        if arcpy.Exists(outputDensity) :
            arcpy.Delete_management(outputDensity)

        # WORKAROUND: Model/Tool uses scratch GDB that may have previous outputs
        arcpy.env.scratchWorkspace = self.incidentScratchGDB
        workaround = os.path.join(self.incidentScratchGDB, 'IncidentDensitySurface_Output')
        if arcpy.Exists(workaround) :
            arcpy.Delete_management(workaround)
        # END WORKAROUND

        arcpy.CheckOutExtension("Spatial")     

        sr = arcpy.SpatialReference(3857) # 'WGS 1984 Web Mercator Auxiliary Sphere'

        try:
            # Tools have different parameter order in Pro vs. ArcMap
            if Configuration.Platform == Configuration.PLATFORM_PRO :
                arcpy.IncidentDensity_iaTools(self.inputPointFeatures, self.inputBoundaryFeatures, \
                    sr, outputDensity)
            else:
                arcpy.IncidentDensity_iaTools(self.inputPointFeatures, self.inputBoundaryFeatures, \
                    outputDensity, sr)
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
        except Exception as e:
            UnitTestUtilities.handleGeneralError(e)

        self.assertTrue(arcpy.Exists(outputDensity))

        arcpy.CheckInExtension("Spatial")

if __name__ == "__main__":
    unittest.main()