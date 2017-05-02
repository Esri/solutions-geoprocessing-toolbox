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
==================================================
'''

import arcpy
import os
import unittest
import UnitTestUtilities
import Configuration
import DataDownload
import arcpyAssert

class CountIncidentsByLOCTestCase(unittest.TestCase, arcpyAssert.FeatureClassAssertMixin):
    ''' Test all tools and methods related to the Count Incidents by LOC tool
    in the Incident Analysis toolbox'''
    
    inputPointsFeatures = None
    inputLinesFeatures = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print(".....CountIncidentsByLOCTestCase.setUp")  
        UnitTestUtilities.checkArcPy()
        
        Configuration.incidentDataPath = DataDownload.runDataDownload(Configuration.patternsPaths, Configuration.incidentGDBName, Configuration.incidentURL)
        if (Configuration.incidentScratchGDB == None) or (not arcpy.Exists(Configuration.incidentScratchGDB)):
            Configuration.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentDataPath)
        Configuration.incidentInputGDB = os.path.join(Configuration.incidentDataPath, Configuration.incidentGDBName)
        Configuration.incidentResultGDB = os.path.join(Configuration.incidentDataPath, Configuration.incidentResultGDBName)
        
        UnitTestUtilities.checkFilePaths([Configuration.incidentDataPath, Configuration.incidentInputGDB, Configuration.patterns_ProToolboxPath, Configuration.patterns_DesktopToolboxPath])
     
        # set up inputs    
        self.inputPointsFeatures = os.path.join(Configuration.incidentInputGDB, "Incidents")
        self.inputLinesFeatures = os.path.join(Configuration.incidentInputGDB, "Roads")
        self.inputAOIFeatures = os.path.join(Configuration.incidentInputGDB, "Districts")
        self.resultCompareFeatures0001 = os.path.join(Configuration.incidentResultGDB, "resultsCountIncidentsByLOC_0001")
            
    def tearDown(self):
        if Configuration.DEBUG == True: print(".....CountIncidentsByLOCTestCase.tearDown")
        UnitTestUtilities.deleteScratch(Configuration.incidentScratchGDB)
        
    def test_count_incidents_pro(self):
        '''test_count_incidents_pro'''
        if Configuration.DEBUG == True: print(".....CountIncidentsByLOCTestCase.test_count_incidents_pro")
        arcpy.ImportToolbox(Configuration.patterns_ProToolboxPath, "iaTools")
        outputCountFeatures = os.path.join(Configuration.incidentScratchGDB, "outputCount")
        runToolMsg = "Running tool (Count Incidents By LOC - Pro)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)
        arcpy.CountIncidentsByLOC_iaTools(self.inputPointsFeatures,
                                          self.inputLinesFeatures,
                                          self.inputAOIFeatures,
                                          outputCountFeatures,
                                          "50 Meters")
        self.assertFeatureClassEqual(self.resultCompareFeatures0001, outputCountFeatures, "OBJECTID")
            
    
    def test_count_incidents_desktop(self):
        if Configuration.DEBUG == True: print(".....CountIncidentsByLOCTestCase.test_count_incidents_desktop")
        arcpy.ImportToolbox(Configuration.patterns_DesktopToolboxPath, "iaTools")
        outputCountFeatures = os.path.join(Configuration.incidentScratchGDB, "outputCount")
        runToolMsg = "Running tool (Count Incidents By LOC - Desktop)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)
        arcpy.CountIncidentsByLOC_iaTools(self.inputPointsFeatures,
                                          self.inputLinesFeatures,
                                          self.inputAOIFeatures,
                                          outputCountFeatures,
                                          "50 Meters")
        self.assertFeatureClassEqual(self.resultCompareFeatures0001,outputCountFeatures,"OBJECTID")
