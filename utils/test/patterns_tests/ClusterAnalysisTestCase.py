# coding: utf-8
# -----------------------------------------------------------------------------
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
# -----------------------------------------------------------------------------

# ==================================================
# ClusterAnalysisTestCase.py
# --------------------------------------------------
# requirements:
# * ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
# * Python 2.7 or Python 3.4
#
# author: ArcGIS Solutions
# company: Esri
#
# ==================================================
# history:
# 12/16/2015 - JH - initial creation
# ==================================================

import arcpy
import os
import unittest
import UnitTestUtilities
import Configuration
import DataDownload

class ClusterAnalysisTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Cluster Analysis tool
    in the Incident Analysis toolbox'''
    
    inputPointsFeatures = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print("     ClusterAnalysisTestCase.setUp")
        UnitTestUtilities.checkArcPy()
        
        Configuration.incidentDataPath = DataDownload.runDataDownload(Configuration.patternsPaths, Configuration.incidentGDBName, Configuration.incidentURL)
        if (Configuration.incidentScratchGDB == None) or (not arcpy.Exists(Configuration.incidentScratchGDB)):
            Configuration.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentDataPath)
        Configuration.incidentInputGDB = os.path.join(Configuration.incidentDataPath, Configuration.incidentGDBName)    
        
        UnitTestUtilities.checkFilePaths([Configuration.incidentDataPath, Configuration.incidentInputGDB, Configuration.patterns_ProToolboxPath, Configuration.patterns_DesktopToolboxPath])
        if (Configuration.incidentScratchGDB == None) or (not arcpy.Exists(Configuration.incidentScratchGDB)):
            Configuration.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentDataPath)
            
        # set up inputs
        self.inputPointsFeatures = os.path.join(Configuration.incidentInputGDB, "Incidents")
        
    def tearDown(self):
        if Configuration.DEBUG == True: print("     ClusterAnalysisTestCase.tearDown")
        UnitTestUtilities.deleteScratch(Configuration.incidentScratchGDB)
        
    def test_cluster_analysis_pro(self):
        arcpy.AddMessage("Testing Cluster Analysis (Pro).")
        self.test_cluster_analysis(Configuration.patterns_ProToolboxPath)
    
    def test_cluster_analysis_desktop(self):
        arcpy.AddMessage("Testing Cluster Analysis (Desktop).")
        self.test_cluster_analysis(Configuration.patterns_DesktopToolboxPath)
        
    def test_cluster_analysis(self, toolboxPath):
        try:
            if Configuration.DEBUG == True: print("     ClusterAnalysisTestCase.test_cluster_analysis")

            arcpy.ImportToolbox(toolboxPath, "iaTools")
            outputClusterFeatures = os.path.join(Configuration.incidentScratchGDB, "outputClusters")

            runToolMessage = "Running tool (Cluster Analysis)"
            arcpy.AddMessage(runToolMessage)
            Configuration.Logger.info(runToolMessage)
            
            # arcpy.ClusterAnalysis_iaTools(self.inputPointsFeatures, Output_Cluster_Features=outputClusterFeatures)
            arcpy.ClusterAnalysis_iaTools(self.inputPointsFeatures, "#", outputClusterFeatures)
            clusterCount = int(arcpy.GetCount_management(outputClusterFeatures).getOutput(0))
            self.assertEqual(clusterCount, int(37))
        
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
            
        except:
            UnitTestUtilities.handleGeneralError()
        
        