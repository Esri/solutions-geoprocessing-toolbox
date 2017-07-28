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
ClusterAnalysisTestCase.py
--------------------------------------------------
requirements:
* ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
* Python 2.7 or Python 3.4

author: ArcGIS Solutions
company: Esri

==================================================
history:
12/16/2015 - JH - initial creation
09/20/2016 - MF - Update to two method test pattern
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

class ClusterAnalysisTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Cluster Analysis tool
    in the Incident Analysis toolbox'''

    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime
    toolboxUnderTestAlias = 'iaTools'

    incidentScratchGDB = None
    inputPointsFeatures = None

    def setUp(self):

        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''

        self.toolboxUnderTest = Configuration.incidentToolboxPath + Configuration.GetToolboxSuffix()

        if Configuration.DEBUG == True: print(".....ClusterAnalysisTestCase.setUp")
        UnitTestUtilities.checkArcPy()

        DataDownload.runDataDownload(Configuration.incidentAnalysisDataPath, Configuration.incidentInputGDB, Configuration.incidentURL)
        if (self.incidentScratchGDB == None) or (not arcpy.Exists(self.incidentScratchGDB)):
            self.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentAnalysisDataPath)

        # set up inputs
        self.inputPointsFeatures = os.path.join(Configuration.incidentInputGDB, "Incidents")

        arcpy.env.OverwriteOutputs = True

        UnitTestUtilities.checkFilePaths([Configuration.incidentAnalysisDataPath])

        UnitTestUtilities.checkGeoObjects([Configuration.incidentInputGDB, \
                                           self.incidentScratchGDB, \
                                           self.toolboxUnderTest, \
                                           self.inputPointsFeatures])

    def tearDown(self):
        if Configuration.DEBUG == True: print(".....ClusterAnalysisTestCase.tearDown")
        UnitTestUtilities.deleteScratch(self.incidentScratchGDB)

    def test_cluster_analysis(self):
        '''test_cluster_analysis'''
        if Configuration.DEBUG == True: print(".....ClusterAnalysisTestCase.test_cluster_analysis")
        arcpy.ImportToolbox(self.toolboxUnderTest, self.toolboxUnderTestAlias)
        outputClusterFeatures = os.path.join(self.incidentScratchGDB, "outputClusters")
        runToolMessage = "Running tool (Cluster Analysis)"
        arcpy.AddMessage(runToolMessage)
        Configuration.Logger.info(runToolMessage)
        try:
            arcpy.ClusterAnalysis_iaTools(self.inputPointsFeatures, outputClusterFeatures)
        except:
            msg = arcpy.GetMessages(2)
            self.fail('Exception in ClusterAnalysis_iaTools toolbox \n' + msg)
        clusterCount = int(arcpy.GetCount_management(outputClusterFeatures).getOutput(0))
        self.assertGreater(clusterCount, int(10))

if __name__ == "__main__":
    unittest.main()