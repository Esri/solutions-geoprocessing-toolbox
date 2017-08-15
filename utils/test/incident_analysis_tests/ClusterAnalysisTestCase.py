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

class ClusterAnalysisTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Cluster Analysis tool
    in the Incident Analysis toolbox'''

    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime
    toolboxUnderTestAlias = 'iaTools'

    inputPointsFeatures = None

    def setUp(self):

        if Configuration.DEBUG == True: print(".....ClusterAnalysisTestCase.setUp")

        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''

        self.toolboxUnderTest = Configuration.incidentToolboxPath + Configuration.GetToolboxSuffix()

        UnitTestUtilities.checkArcPy()

        DataDownload.runDataDownload(Configuration.incidentAnalysisDataPath, Configuration.incidentInputGDB, Configuration.incidentURL)

        # set up inputs
        self.inputPointsFeatures = os.path.join(Configuration.incidentInputGDB, "Incidents")

        arcpy.env.OverwriteOutputs = True

        UnitTestUtilities.checkFilePaths([Configuration.incidentAnalysisDataPath])

        UnitTestUtilities.checkGeoObjects([Configuration.incidentInputGDB, \
                                           Configuration.incidentResultGDB, \
                                           self.toolboxUnderTest, \
                                           self.inputPointsFeatures])

    def tearDown(self):
        if Configuration.DEBUG == True: print(".....ClusterAnalysisTestCase.tearDown")

    def test_cluster_analysis(self):
        '''test_cluster_analysis'''
        if Configuration.DEBUG == True: print(".....ClusterAnalysisTestCase.test_cluster_analysis")
        arcpy.ImportToolbox(self.toolboxUnderTest, self.toolboxUnderTestAlias)

        outputClusterFeatures = os.path.join(Configuration.incidentResultGDB, "outputClusters")

        # Delete the feature class used to load if already exists
        if arcpy.Exists(outputClusterFeatures) :
            arcpy.Delete_management(outputClusterFeatures)

        runToolMessage = "Running tool (Cluster Analysis)"
        arcpy.AddMessage(runToolMessage)
        Configuration.Logger.info(runToolMessage)        
        distance = "500 Meters"

        try:
            # Tools have different parameter order in Pro vs. ArcMap
            if Configuration.Platform == Configuration.PLATFORM_PRO :
                arcpy.ClusterAnalysis_iaTools(self.inputPointsFeatures, distance, outputClusterFeatures)
            else:
                arcpy.ClusterAnalysis_iaTools(self.inputPointsFeatures, outputClusterFeatures, distance)
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
        except Exception as e:
            UnitTestUtilities.handleGeneralError(e)

        clusterCount = int(arcpy.GetCount_management(outputClusterFeatures).getOutput(0))
        self.assertGreaterEqual(clusterCount, int(10))

if __name__ == "__main__":
    unittest.main()