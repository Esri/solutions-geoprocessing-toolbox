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
        try:
            UnitTestUtilities.checkArcPy()
            paths = [TestUtilities.vis_GeodatabasePath, TestUtilities.vis_ToolboxesPath]
            UnitTestUtilities.checkFilePaths(paths)
            geoObjects = [TestUtilities.sunPosToolbox, TestUtilities.vis_inputGDB, TestUtilities.vis_inputArea, TestUtilities.vis_inputSurface, TestUtilities.vis_compareResults]
            UnitTestUtilities.checkGeoObjects(geoObjects)
            UnitTestUtilities.createScratch(TestUtilities.vis_ScratchPath)
            
            
        except arcpy.ExecuteError: 
            # Get the arcpy error messages
            msgs = arcpy.GetMessages()
            arcpy.AddError(msgs)
            print(msgs)

            # return a system error code
            sys.exit(-1)
            
        except:
            # Get the traceback object
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]

            # Concatenate information together concerning the error into a message string
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n"\
                + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

            # Return python error messages for use in script tool or Python Window
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)

            # Print Python error messages for use in Python / Python Window
            print(pymsg + "\n")
            print(msgs)

            # return a system error code
            sys.exit(-1)
            