
import unittest
import logging
import arcpy
from arcpy.sa import *
import sys
import traceback
import datetime
import os
import TestUtilities
import UnitTestUtilities
                
                
class SunPositionAndHillshadeUnitTest(unittest.TestCase):
    def setUp(self):
        # set-up code
        arcpy.AddMessage("Setting up SunPositionAndHillshadeUnitTest.")
        UnitTestUtilities.checkArcPy()
        
        # WORKAROUND: delete scratch db (having problems with scratch read-only "scheme lock" errors
        # print "Deleting Scratch Workspace (Workaround)"    
        # TestUtilities.deleteScratch()
        if not arcpy.Exists(TestUtilities.scratchGDB):
            UnitTestUtilities.createScratch()
        UnitTestUtilities.checkFilePaths()
        UnitTestUtilities.checkGeoObjects()
     
    # def tearDown(self):
        # # tear-down code
        # arcpy.AddMessage("Tearing down the SunPositionAndHillshadeUnitTest.")
        
    def test_sun_position_analysis(self):
        try:
            arcpy.AddMessage("Testing Sun Position Analysis (unit).")
            # move TestSunPositionAndHillshade code in here
            print("Importing toolbox... ")
            arcpy.ImportToolbox(TestUtilities.toolbox, "sunpos")
            arcpy.env.overwriteOutput = True

            # Inputs
            print("Setting up inputs... ")
            # '''
            # Tool comparison is based on static dataset in Web Mercator
            # over Afghanistan, for 7/30/2015 at 14:28:36.
            # '''
            dtCompare = datetime.datetime(2015, 7, 30, 14, 28, 36)
            print("Set date...")
            utcAfghanistan = r'(UTC+4:30) Afghanistan'
            print("Set UTCAfg...")
            outHillshade = os.path.join(TestUtilities.outputGDB, "outputHS")
            print("Set output hillshade...")

            # Testing
            arcpy.AddMessage("Running tool (Sun Position and Hillshade)")
            arcpy.SunPositionAnalysis_sunpos(TestUtilities.inputArea, TestUtilities.inputSurface, dtCompare, utcAfghanistan, outHillshade)

            print("Comparing expected values with tool results from " + str(dtCompare)\
                + " in " + str(utcAfghanistan))
            compareResults = TestUtilities.compareResults

            arcpy.CheckOutExtension("Spatial")
            diff = Minus(Raster(outHillshade),Raster(compareResults))
            diff.save(os.path.join(TestUtilities.scratchGDB, "diff"))
            arcpy.CalculateStatistics_management(diff)
            rasMinimum = float(arcpy.GetRasterProperties_management(diff,"MINIMUM").getOutput(0))
            rasMaximum = float(arcpy.GetRasterProperties_management(diff,"MAXIMUM").getOutput(0))
            rasMean = float(arcpy.GetRasterProperties_management(diff,"MEAN").getOutput(0))
            rasSTD = float(arcpy.GetRasterProperties_management(diff,"STD").getOutput(0))
            rasUnique = int(arcpy.GetRasterProperties_management(diff,"UNIQUEVALUECOUNT").getOutput(0))

            self.assertEqual(rasMaximum, float(0))
            self.assertEqual(rasMinimum, float(0))
            self.assertEqual(rasUnique, int(1))
            
            # if (rasMaximum == float(0)) and (rasMinimum == float(0)) and (rasUnique == int(1)):
                # print("No differences between tool output and expected results.")
                # print("Test Passed")
            # else:
                # msg = "ERROR IN TOOL RESULTS: \n"\
                    # + "Difference between tool output and expected results found:\n"\
                    # + "Difference Minimum: " + str(rasMinimum) + "\n"\
                    # + "Difference Maximum: " + str(rasMaximum) + "\n"\
                    # + "Difference Mean: " + str(rasMean) + "\n"\
                    # + "Difference Std. Deviation: " + str(rasSTD) + "\n"\
                    # + "Difference Number of Unique Values: " + str(rasUnique) + "\n"
                # raise ValueDifferenceError(msg)
        
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
            
        finally:
            arcpy.CheckInExtension("Spatial")
        
        
