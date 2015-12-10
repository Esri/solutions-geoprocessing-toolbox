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
# CountIncidentsByLOCTestCase.py
# --------------------------------------------------
# requirments: ArcGIS X.X, Python 2.7 or Python 3.4
# author: ArcGIS Solutions
# contact: ArcGISTeam<Solution>@esri.com
# company: Esri
# ==================================================
# description: <Description>
# ==================================================
# history:
# <date> - <initals> - <modifications>
# ==================================================

import arcpy
import os
import unittest
import TestUtilities
import UnitTestUtilities


#class HLZTouchdownPoints(UnitTestCase.UnitTestCase):
class CountIncidentsByLOC(unittest.TestCase):
    ''' Test all tools and methods related to the HLZ Touchdown Points tool
    in the Helicopter Landing Zones toolbox'''

    scratchGDB = None

    tbxProFolderPath = os.path.join(TestUtilities.repoPath, "patterns", "toolboxes", "Incident Analysis Tools.tbx")
    tbxDesktopFolderPath = os.path.join(TestUtilities.repoPath, "patterns", "toolboxes", "Incident Analysis Tools_10.3.tbx")
    testDataFolderPath = os.path.join(TestUtilities.patternsPaths, "data")

    inputAirframeTable = None
    inputSuitableAreas = None
    inputSlope = None
    outputGeodatabase = None
    outputCenterpoints = None
    outputCircles = None

    def setUp(self):
        ''' set-up code '''

        UnitTestUtilities.checkArcPy()
        UnitTestUtilities.checkFilePaths([self.testDataFolderPath,
                                          self.tbxProFolderPath,
                                          self.tbxDesktopFolderPath])

        self.testDataGeodatabase = os.path.join(self.testDataFolderPath, r"test_hlz_tools.gdb")

        # Check the test inputs (do they exist? or not?)
        if (self.scratchGDB == None) or (not arcpy.Exists(self.scratchGDB)):
            self.scratchGDB = UnitTestUtilities.createScratch(self.testDataFolderPath)

        # Setup the test inputs

        UnitTestUtilities.checkGeoObjects([])
        return

    def tearDown(self):
        ''' clean up after tests'''
        UnitTestUtilities.deleteScratch(self.scratchGDB)
        return


    def test_CountIncidentsByLOC001_Pro(self):
        ''' '''
        self.CountIncidentsByLOC001()
        return

    def test_CountIncidentsByLOC001_Desktkop(self):
        ''' '''
        self.CountIncidentsByLOC001()
        return

    def CountIncidentsByLOC001(self):
        ''' '''
        return
