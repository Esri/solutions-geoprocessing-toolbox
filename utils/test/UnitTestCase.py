#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------

import sys
import arcpy
import unittest
import TestUtilities
import UnitTestUtilities

class UnitTestCase(unittest.TestCase):
    def setUp(self):
        UnitTestUtilities.checkArcPy()
        visibility_Paths = [TestUtilities.vis_GeodatabasePath, TestUtilities.vis_ToolboxesPath, TestUtilities.sunPosToolbox, TestUtilities.visandRangeToolbox]
        UnitTestUtilities.checkFilePaths(visibility_Paths)
  