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
# requirments: ArcGIS X.X, Python 2.7 or Python 3.4
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

class ClusterAnalysisTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Cluster Analysis tool
    in the Incident Analysis toolbox'''
    
    proToolboxPath = os.path.join(Configuration.patterns_ToolboxesPath, "Incident Analysis Tools.tbx")
    desktopToolboxPath = os.path.join(Configuration.patterns_ToolboxesPath, "Incident Analysis Tools_10.4.tbx")
    scratchGDB = None
    incidentDataPath = os.path.join(Configuration.patternsPaths, "data")
    
    incidentGDB = os.path.join(incidentDataPath, "IncidentAnalysis.gdb")
    inputPointsFeatures = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print("     ClusterAnalysisTestCase.setUp")
        UnitTestUtilities.checkArcPy()
        UnitTestUtilities.checkFilePaths([self.incidentDataPath, self.proToolboxPath, self.desktopToolboxPath])
        if (self.scratchGDB == None) or (not arcpy.Exists(self.scratchGDB)):
            self.scratchGDB = UnitTestUtilities.createScratch(self.incidentDataPath)
            
        # set up inputs
        self.inputPointsFeatures = os.path.join(self.incidentGDB, "Incidents")
        
    def tearDown(self):
        if Configuration.DEBUG == True: print("     ClusterAnalysisTestCase.tearDown")
        # UnitTestUtilities.deleteScratch(self.scratchGDB)
        
    def test_cluster_analysis_pro(self):
        arcpy.AddMessage("Testing Cluster Analysis (Pro).")
        self.test_cluster_analysis(self.proToolboxPath)
    
    def test_cluster_analysis_desktop(self):
        arcpy.AddMessage("Testing Cluster Analysis (Desktop).")
        self.test_cluster_analysis(self.desktopToolboxPath)
        
    def test_cluster_analysis(self, toolboxPath):
        try:
            if Configuration.DEBUG == True: print("     ClusterAnalysisTestCase.test_cluster_analysis")
            # import the toolbox
            arcpy.ImportToolbox(toolboxPath, "iaTools")
            
            # set up variables 
            clusterDistance = 500
            outputClusterFeatures = os.path.join(self.scratchGDB, "outputClusters")

            arcpy.ClusterAnalysis_iaTools(self.inputPointsFeatures, clusterDistance, outputClusterFeatures)
            clusterCount = int(arcpy.GetCount_management(outputClusterFeatures).getOutput(0))
            self.assertEqual(clusterCount, int(37))
        
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
            
        except:
            UnitTestUtilities.handleGeneralError()
        
        