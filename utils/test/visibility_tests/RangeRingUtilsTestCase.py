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
RangeRingUtilsTestCase.py
--------------------------------------------------
requirements: ArcGIS X.X, Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
description: unittest test case for Range Rings
==================================================
history:
03/30/2016 - mf - initial coding
04/07/2016 - mf - fit RR tests into s-g-t unit test stuff
==================================================
'''
import os
import sys
import arcpy
import unittest
import datetime
import logging
import Configuration
import UnitTestUtilities
import DataDownload

# ============================================================================
# Add RangeRingUtils.py module to python path
currentPath = os.path.dirname(__file__)
pathToRRUtils= os.path.normpath(os.path.join(currentPath, r"../../../visibility/toolboxes/scripts"))
sys.path.insert(0, pathToRRUtils)
import RangeRingUtils
# ============================================================================

class RangeRingUtilsTestCase(unittest.TestCase):
    ''' Test all methods and classes in RangeRingUtils.py '''

    def setUp(self):
        ''' setup for tests'''
        if Configuration.DEBUG == True: print("         RangeRingsUtilsTestCase.setUp")

        UnitTestUtilities.checkArcPy()
        self.proToolboxPath = os.path.join(Configuration.vis_ToolboxesPath,
                                           "Visibility and Range Tools.tbx")
        self.desktopToolboxPath = os.path.join(Configuration.vis_ToolboxesPath,
                                               "Visibility and Range Tools_10.4.tbx")
        self.srWebMerc = arcpy.SpatialReference(3857) #WGS_1984_Web_Mercator
        self.srWGS84 = arcpy.SpatialReference(4326) #GCS_WGS_1984
        self.srWAZED = arcpy.SpatialReference(54032) #World_Azimuthal_Equidistant
        self.deleteme = []

        self.DataGDB = None
        self.rrDataPath = os.path.join(Configuration.visibilityPaths, 'data')
        if (self.DataGDB == None) or (not arcpy.Exists(self.DataGDB)):
            self.DataGDB = UnitTestUtilities.createScratch(self.rrDataPath)

        UnitTestUtilities.checkFilePaths([self.proToolboxPath,
                                          self.desktopToolboxPath,
                                          Configuration.visibilityPaths,
                                          self.rrDataPath,
                                          self.DataGDB])


        #create a temp point feature class
        ptCoords = [[0.0, 0.0], [10.0, 10.0], [3.0, 3.0], [5.5, 1.5]]
        tempfcPath = os.path.join("in_memory", "tempfc")
        if arcpy.Exists(tempfcPath):
            arcpy.Delete_management(tempfcPath)
        self.pointGeographic = arcpy.CreateFeatureclass_management(os.path.dirname(tempfcPath),
                                                                   os.path.basename(tempfcPath),
                                                                   "POINT", "#", "DISABLED",
                                                                   "DISABLED", self.srWGS84)[0]
        with arcpy.da.InsertCursor(self.pointGeographic, ["SHAPE@XY"]) as cursor:
            for (x, y) in ptCoords:
                cursor.insertRow([(x, y)])
        del cursor
        self.deleteme.append(self.pointGeographic)
        return

    def tearDown(self):
        ''' cleanup after tests'''
        if Configuration.DEBUG == True: print("         RangeRingsUtilsTestCase.tearDown")
        del self.pointGeographic
        for i in self.deleteme:
            if arcpy.Exists(i):
                arcpy.Delete_management(i)
        return

    def test_RingMaker_init(self):
        ''' test class'''
        print("RangeRingsUtilsTestCase.test_RingMaker_init")
        ringDistanceList = [10.0, 20.0, 30.0, 40.0]
        rm = RangeRingUtils.RingMaker(self.pointGeographic,
                                      ringDistanceList,
                                      "METERS",
                                      self.srWAZED)
        self.assertEquals(rm.ringCount, len(ringDistanceList))
        self.assertEquals(rm.ringMin, 10.0)
        self.assertEquals(rm.ringMax, 40.0)
        return

    #TODO: test init with empty ring list (no values)
    #TODO: test init with negative rings (bad values)
    #TODO: test init with empty point features (empty)
    #TODO: test init with polyline or polygon inputs (wrong type)

    def test_RingMaker_sortList_empty(self):
        ''' test RingMaker's internal _sortList method if it handles an empty list'''
        print("RangeRingsUtilsTestCase.test_RingMaker_sortList_emtpy")
        rm = RangeRingUtils.RingMaker(self.pointGeographic, [10.0, 20.0], "METERS", self.srWAZED)
        outList = rm._sortList([])
        self.assertIsNone(outList)
        return

    def test_RingMaker_sortList_isSorted(self):
        ''' test Ringmaker's internal _sortedList method if it sorts a list'''
        print("RangeRingsUtilsTestCase.test_sortList_isSorted")
        l = [7, 5, 9, 3, 8, 1, 6, 2, 4, 0]
        rm = RangeRingUtils.RingMaker(self.pointGeographic, [10.0, 20.0], "METERS", self.srWAZED)
        outList = rm._sortList(l)
        self.assertEqual(outList, sorted(l))
        return

    def test_RingMaker_addFieldsToTable(self):
        ''' test RingMaker's internal _addFieldsToTable method'''
        print("RangeRingsUtilsTestCase.test_RingMaker_addFieldsToTable")
        fc = arcpy.CreateFeatureclass_management("in_memory", "fcTestFields", "POINT")[0]
        numFieldsBefore = len(arcpy.ListFields(fc))

        fields = {"a":"DOUBLE", "b":"TEXT"}
        rm = RangeRingUtils.RingMaker(self.pointGeographic, [10.0, 20.0], "METERS", self.srWAZED)
        newfc = rm._addFieldsToTable(fc, fields)
        numFieldsAfter = len(list(arcpy.ListFields(newfc)))

        self.assertEqual(numFieldsAfter, numFieldsBefore + 2)
        self.deleteme.append(fc)
        return

    def test_RingMaker_makeTempTable(self):
        ''' test RingMaker's internal method'''
        print("RangeRingsUtilsTestCase.test_RingMaker_makeTempTable")
        rm = RangeRingUtils.RingMaker(self.pointGeographic, [10.0, 20.0], "METERS", self.srWAZED)
        tempTab = rm._makeTempTable("tempTab", {"a":"TEXT"})
        self.assertTrue(arcpy.Exists(tempTab))
        self.deleteme.append(tempTab)
        return

    def test_RingMaker_makeRingsFromDistances(self):
        ''' test RingMaker's internal method'''
        print("RangeRingsUtilsTestCase.test_RingMaker_makeRingsFromDistances")
        ringDistanceList = [10.0, 20.0, 30.0, 40.0]
        ringCountEstimate = len(ringDistanceList) * int(arcpy.GetCount_management(self.pointGeographic).getOutput(0))
        rm = RangeRingUtils.RingMaker(self.pointGeographic, ringDistanceList, "METERS", self.srWAZED)
        rm.makeRingsFromDistances()
        ringCountActual = int(arcpy.GetCount_management(rm.ringFeatures).getOutput(0))
        self.assertEqual(ringCountEstimate, ringCountActual)
        return

    def test_RingMaker_makeRadials(self):
        ''' test RingMaker's internal method'''
        print("RangeRingsUtilsTestCase.test_RingMaker_makeRadials")
        ringDistanceList = [10.0, 20.0, 30.0, 40.0]
        rm = RangeRingUtils.RingMaker(self.pointGeographic, ringDistanceList,
                                      "METERS", self.srWAZED)
        radialsToMake = 8
        radialCountEstimate = radialsToMake * int(arcpy.GetCount_management(self.pointGeographic).getOutput(0))
        rm.makeRadials(radialsToMake)
        radialCountActual = int(arcpy.GetCount_management(rm.radialFeatures).getOutput(0))
        self.assertEqual(radialCountEstimate, radialCountActual)
        return

    def test_RingMaker_saveRingsAsFeatures(self):
        ''' test RingMaker's internal method'''
        print("RangeRingsUtilsTestCase.test_RingMaker_saveRingsAsFeatures")
        ringDistanceList = [10.0, 20.0, 30.0, 40.0]
        rm = RangeRingUtils.RingMaker(self.pointGeographic, ringDistanceList,
                                      "METERS", self.srWAZED)
        rm.makeRingsFromDistances()
        tempRings = os.path.join(self.DataGDB, "tempRings")
        if arcpy.Exists(tempRings): arcpy.Delete_management(tempRings)
        ringFeatures = rm.saveRingsAsFeatures(tempRings)
        self.assertTrue(arcpy.Exists(ringFeatures))
        self.deleteme.append(ringFeatures)
        return

    def test_RingMaker_saveRadialsAsFeatures(self):
        ''' test saving raidal features to feature class'''
        print("RangeRingsUtilsTestCase.test_RingMaker_saveRadialsAsFeatures")
        ringDistanceList = [10.0, 20.0, 30.0, 40.0]
        rm = RangeRingUtils.RingMaker(self.pointGeographic, ringDistanceList,
                                      "METERS", self.srWAZED)
        rm.makeRadials(4)
        tempRadials = os.path.join(self.DataGDB, "tempRadials")
        if arcpy.Exists(tempRadials): arcpy.Delete_management(tempRadials)
        radialFeatures = rm.saveRadialsAsFeatures(tempRadials)
        self.assertTrue(arcpy.Exists(radialFeatures))
        self.deleteme.append(radialFeatures)
        return

    #=== TEST TOOL METHODS ==========================================

    def test_rangeRingsFromMinMax(self):
        ''' testing the tool method '''
        print("RangeRingsUtilsTestCase.test_rangeRingsFromMinMax")
        numCenters = int(arcpy.GetCount_management(self.pointGeographic).getOutput(0))
        numRadials = 8
        rings = os.path.join(self.DataGDB, "newRings")
        radials = os.path.join(self.DataGDB, "newRadials")
        rr = RangeRingUtils.rangeRingsFromMinMax(self.pointGeographic,
                                                 100.0,
                                                 1000.0,
                                                 "METERS",
                                                 numRadials,
                                                 rings,
                                                 radials,
                                                 self.srWAZED)
        outRings = rr[0]
        outRadials = rr[1]

        self.assertTrue(arcpy.Exists(outRings))
        self.assertEqual(int(arcpy.GetCount_management(outRings).getOutput(0)), numCenters * 2)

        self.assertTrue(arcpy.Exists(outRadials))
        self.assertEqual(int(arcpy.GetCount_management(outRadials).getOutput(0)), numRadials * numCenters)

        self.deleteme.append(rings)
        self.deleteme.append(radials)
        return

    def test_rangeRingsFromList(self):
        ''' testing rangeRingsFromList method'''
        print("RangeRingsUtilsTestCase.test_rangeRingsFromList")
        numCenters = int(arcpy.GetCount_management(self.pointGeographic).getOutput(0))
        numRadials = 8
        rings = os.path.join(self.DataGDB, "newRings")
        radials = os.path.join(self.DataGDB, "newRadials")
        ringList = [1.0, 3.0, 9.0, 27.0, 81.0, 243.0, 729.0]
        rr = RangeRingUtils.rangeRingsFromList(self.pointGeographic,
                                               ringList,
                                               "METERS",
                                               numRadials,
                                               rings,
                                               radials,
                                               self.srWAZED)
        outRings = rr[0]
        outRadials = rr[1]

        self.assertTrue(arcpy.Exists(outRings))
        self.assertEqual(int(arcpy.GetCount_management(outRings).getOutput(0)), len(ringList) * numCenters)

        self.assertTrue(arcpy.Exists(outRadials))
        self.assertEqual(int(arcpy.GetCount_management(outRadials).getOutput(0)), numRadials * numCenters)

        self.deleteme.append(rings)
        self.deleteme.append(radials)
        return

    def test_rangeRingsFromInterval(self):
        ''' testing rangeRingsFromInterval method'''
        print("RangeRingsUtilsTestCase.test_rangeRingsFromInterval")
        numCenters = int(arcpy.GetCount_management(self.pointGeographic).getOutput(0))
        numRadials = 8
        rings = os.path.join(self.DataGDB, "newRings")
        radials = os.path.join(self.DataGDB, "newRadials")
        numRings = 4
        distanceBetween = 200.0
        rr = RangeRingUtils.rangeRingsFromInterval(self.pointGeographic,
                                                   numRings,
                                                   distanceBetween,
                                                   "METERS",
                                                   numRadials,
                                                   rings,
                                                   radials,
                                                   self.srWAZED)
        outRings = rr[0]
        outRadials = rr[1]

        self.assertTrue(arcpy.Exists(outRings))
        self.assertEqual(int(arcpy.GetCount_management(outRings).getOutput(0)), 4 * numCenters)

        self.assertTrue(arcpy.Exists(outRadials))
        self.assertEqual(int(arcpy.GetCount_management(outRadials).getOutput(0)), numRadials * numCenters)

        self.deleteme.append(rings)
        self.deleteme.append(radials)
        return
