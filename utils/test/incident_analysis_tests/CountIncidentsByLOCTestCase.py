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
CountIncidentsByLOCTestCase.py
--------------------------------------------------
requirments: ArcGIS X.X, Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
history:
12/16/2015 - JH - initial creation
09/20/2016 - MF - Update to two method test pattern
05/02/2017 - MF - Update test for new AOI parameter in the tool
07/28/2017 - CM - Refactor
==================================================
'''

import arcpy
import os
import unittest

# Add parent folder to python path if running test case standalone
import sys
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import UnitTestUtilities
import Configuration
import DataDownload
import arcpyAssert

class CountIncidentsByLOCTestCase(unittest.TestCase, arcpyAssert.FeatureClassAssertMixin):
    ''' Test all tools and methods related to the Count Incidents by LOC tool
    in the Incident Analysis toolbox'''
   
    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime
    toolboxUnderTestAlias = 'iaTools'
     
    inputPointsFeatures = None
    inputLinesFeatures = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print(".....CountIncidentsByLOCTestCase.setUp")  

        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''

        self.toolboxUnderTest = Configuration.incidentToolboxPath + Configuration.GetToolboxSuffix()

        UnitTestUtilities.checkArcPy()
        
        DataDownload.runDataDownload(Configuration.incidentAnalysisDataPath, Configuration.incidentInputGDB, Configuration.incidentURL)
        
        # set up inputs    
        self.inputPointsFeatures = os.path.join(Configuration.incidentInputGDB, "Incidents")
        self.inputLinesFeatures = os.path.join(Configuration.incidentInputGDB, "Roads")
        self.inputAOIFeatures = os.path.join(Configuration.incidentInputGDB, "Districts")
        self.resultCompareFeatures0001 = os.path.join(Configuration.incidentResultGDB, "resultsCountIncidentsByLOC_0001")

        UnitTestUtilities.checkFilePaths([Configuration.incidentAnalysisDataPath])

        UnitTestUtilities.checkGeoObjects([Configuration.incidentInputGDB, \
                                           Configuration.incidentResultGDB, \
                                           self.toolboxUnderTest, \
                                           self.inputPointsFeatures, \
                                           self.inputLinesFeatures,  \
                                           self.inputAOIFeatures,  \
                                           self.resultCompareFeatures0001])
            
    def tearDown(self):
        if Configuration.DEBUG == True: print(".....CountIncidentsByLOCTestCase.tearDown")
        
    def test_count_incidents(self):
        '''test_count_incidents'''
        if Configuration.DEBUG == True: print(".....CountIncidentsByLOCTestCase.test_count_incidents")

        outputCountFeatures = os.path.join(Configuration.incidentResultGDB, "outputCount")

        # Delete the feature class used to load if already exists
        if arcpy.Exists(outputCountFeatures) :
            arcpy.Delete_management(outputCountFeatures)

        arcpy.ImportToolbox(self.toolboxUnderTest, self.toolboxUnderTestAlias)

        runToolMsg = "Running tool (Count Incidents By LOC)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)

        # IMPORTANT: Parameters are different between ArcMap and Pro, differences:
        # 1. Parameter order in Pro ?!
        # 2. Pro *only* takes a feature layer because of differences in behavior 
        #    of Select Layer By Location tool in ArcMap/Pro
        if Configuration.Platform == Configuration.PLATFORM_PRO :

            linesLayer = arcpy.MakeFeatureLayer_management(self.inputLinesFeatures)
            arcpy.CountIncidentsByLOC_iaTools(self.inputPointsFeatures,
                                              linesLayer,
                                              # self.inputLinesFeatures,
                                              self.inputAOIFeatures,
                                              "50 Meters",
                                              outputCountFeatures)
            # Note: Pro and ArcMap returning different results so will test Pro differently            result = arcpy.GetCount_management(outputCountFeatures)
            featureCount = int(arcpy.GetCount_management(outputCountFeatures).getOutput(0))
            print("Number of features in output: " + str(featureCount))
            self.assertGreater(featureCount, int(2000))

        else:

            arcpy.CountIncidentsByLOC_iaTools(self.inputPointsFeatures,
                                              self.inputLinesFeatures,
                                              self.inputAOIFeatures,
                                              outputCountFeatures,
                                              "50 Meters")
            self.assertFeatureClassEqual(self.resultCompareFeatures0001, outputCountFeatures, "OBJECTID")

if __name__ == "__main__":
    unittest.main()
