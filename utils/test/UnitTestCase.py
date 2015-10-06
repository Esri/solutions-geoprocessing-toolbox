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
import UnitTestUtilities

class UnitTestCase(unittest.TestCase):
    def setUp(self):
        try:
            UnitTestUtilities.checkArcPy()
            UnitTestUtilities.createScratch()
            
            # WORKAROUND: delete scratch db (having problems with scratch read-only "scheme lock" errors
            # print "Deleting Scratch Workspace (Workaround)"    
            # TestUtilities.deleteScratch()
            # if not arcpy.Exists(TestUtilities.scratchGDB):
                # print("Creating scratch geodatabase...")
                # UnitTestUtilities.createScratch()
            UnitTestUtilities.checkFilePaths()
            UnitTestUtilities.checkGeoObjects()
            
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
            