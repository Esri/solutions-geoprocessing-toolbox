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
IncidentHotSpotsTestCase.py
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

class IncidentHotSpotsTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Incident Hot Spots tool
    in the Incident Analysis toolbox'''
    
    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime
    toolboxUnderTestAlias = 'iaTools'

    inputPointFeatures = None
    inputBoundaryFeatures = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print(".....IncidentHotSpotsTestCase.setUp")

        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''

        self.toolboxUnderTest = Configuration.incidentToolboxPath + Configuration.GetToolboxSuffix()

        UnitTestUtilities.checkArcPy()

        arcpy.env.OverwriteOutputs = True
        
        DataDownload.runDataDownload(Configuration.incidentAnalysisDataPath, Configuration.incidentInputGDB, Configuration.incidentURL)

        self.inputPointFeatures = os.path.join(Configuration.incidentInputGDB, "Incidents")
        self.inputBoundaryFeatures = os.path.join(Configuration.incidentInputGDB, "Districts")

        UnitTestUtilities.checkFilePaths([Configuration.incidentAnalysisDataPath])

        UnitTestUtilities.checkGeoObjects([Configuration.incidentInputGDB, \
                                           Configuration.incidentResultGDB, \
                                           self.toolboxUnderTest, \
                                           self.inputPointFeatures, \
                                           self.inputBoundaryFeatures])
            
    def tearDown(self):
        if Configuration.DEBUG == True: print(".....IncidentHotSpotsTestCase.tearDown")
        
    def test_incident_hot_spots(self):
        '''test_incident_hot_spots'''
        if Configuration.DEBUG == True: print(".....IncidentHotSpotsTestCase.test_incident_hot_spots")

        arcpy.ImportToolbox(self.toolboxUnderTest, self.toolboxUnderTestAlias)

        runToolMessage = "Running tool (Incident Hot Spots)"
        arcpy.AddMessage(runToolMessage)
        Configuration.Logger.info(runToolMessage)

        outputFeatures = os.path.join(Configuration.incidentResultGDB, "outputHotSpots")

        # Delete the feature class used to load if already exists
        if arcpy.Exists(outputFeatures) :
            arcpy.Delete_management(outputFeatures)

        try:
            if Configuration.Platform == Configuration.PLATFORM_PRO :

                # Pro requires these to be layers
                incidentsLayer = arcpy.MakeFeatureLayer_management(self.inputPointFeatures)
                boundariesLayer = arcpy.MakeFeatureLayer_management(self.inputBoundaryFeatures)

                arcpy.IncidentHotSpots_iaTools(incidentsLayer, boundariesLayer, outputFeatures)
            else:
                # Note: ArcMap has different parameter order
                arcpy.IncidentHotSpots_iaTools(self.inputPointFeatures, outputFeatures, \
                    self.inputBoundaryFeatures)

        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
        except Exception as e:
            UnitTestUtilities.handleGeneralError(e)

        result = arcpy.GetCount_management(outputFeatures)
        featureCount = int(result.getOutput(0))

        print("Number of features in output: " + str(featureCount))

        # Note: Pro and ArcMap returning different counts (4200 vs. 7400)
        self.assertGreater(featureCount, int(4000))

if __name__ == "__main__":
    unittest.main()