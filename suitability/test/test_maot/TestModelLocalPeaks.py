#------------------------------------------------------------------------------
# Copyright 2013 Esri
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
# Name: TestModelLocalPeaks.py
# Description: Automatic Test of Local Peaks Model
# Requirements: ArcGIS Desktop Standard with Spatial Analyst Extension
#------------------------------------------------------------------------------

import arcpy
import os
import sys
import traceback
import TestUtilities

def CellSize(fc):
    ''' get 2000th of the larger of height or width of extent'''
    cs = None
    mx = max(arcpy.Describe(fc).extent.height,arcpy.Describe(fc).extent.width)
    cs = mx/2000.0
    return cs

def RunTest():
    try:
        arcpy.AddMessage("Starting Test: TestLocalPeaks")

        #TEST_IMPLEMENTED = False
        #
        #if not TEST_IMPLEMENTED :
        #    arcpy.AddWarning("***Test Not Yet Implemented***")
        #    return

        # TODO: once model has a version that works with local surface data 
        # (rather than image service), then finish this test/implementation below
        #
        # alternately you can add an image service connection in Catalog and 
        # fill in the parameter below

        if arcpy.CheckExtension("Spatial") == "Available":
            print("Checking out Spatial Analyst license...")
            arcpy.CheckOutExtension("Spatial")
        else:
            # Raise a custom exception
            raise Exception("LicenseError")

        if arcpy.CheckExtension("3D") == "Available":
            print("Checking out 3D Analyst license...")
            arcpy.CheckOutExtension("3D")
        else:
            raise Exception("LicenseError")

        try:
            print("Getting Advanced license...")
            import arcinfo
        except ImportError:
            print("Could not use ArcGIS Advanced license...")
            raise Exception
        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = TestUtilities.scratchGDB

        # WORKAROUND
        print("Creating New Scratch Workspace (Workaround)")
        TestUtilities.createScratch()

        # Getting inputs
        print("Getting inputs...")
        print("inputPolygonFC...")
        inputPolygonFC = os.path.join(TestUtilities.inputGDB, "samplePolygonArea")
        print("inputSurface...")
        inputSurface = TestUtilities.inputElevationURL
        print("outputPointsFC")
        outputPointsFC = os.path.join(TestUtilities.outputGDB, "LocalPeaks")
        print("ImportToolbox--MAoT...")
        arcpy.ImportToolbox(TestUtilities.toolbox, "MAoT")

        # mf - these have been tested
        # # Check For Valid Input
        # print("Checking valid inputs...")
        # objects2Check = []
        # #objects2Check.extend([inputPolygonFC, inputSurface, toolbox])
        # objects2Check.extend([inputPolygonFC, toolbox])
        # for object2Check in objects2Check :
        #     desc = arcpy.Describe(object2Check)
        #     if desc == None :
        #         raise Exception("Bad Input")
        #     else :
        #         print("Valid Object: " + desc.Name)

        # Set environment settings
        print("Running from: " + str(TestUtilities.currentPath))
        print("Geodatabase path: " + str(TestUtilities.geodatabasePath))
        inputFeatureCount = int(arcpy.GetCount_management(inputPolygonFC).getOutput(0)) 
        print("Input FeatureClass: " + str(inputPolygonFC))
        print("Input Feature Count: " +  str(inputFeatureCount))
        # if (inputFeatureCount < 1):
        #     print("Invalid Input Polygon Feature Count: " +  str(inputFeatureCount))

        # Convert input elevation service to local dataset surface
        print("Converting input image service into a local raster surface")
        polygonExtent = arcpy.Describe(inputPolygonFC).extent
        print("Using extent: " + str(polygonExtent))
        cellSize = CellSize(inputPolygonFC)
        print("Using cell size: " + str(cellSize))
        localSurf = None
        srWGS84 = arcpy.SpatialReference(4326) # GCS_WGS_1984
        srWebMerc = arcpy.SpatialReference(3857) #Web_Mercator_Auxiliary_Sphere
        print("Reworking inputs from image service...")
        try:
            tempClipExtent = os.path.join(TestUtilities.scratchGDB,"tempClipExtent")
            localSurf = os.path.join(TestUtilities.scratchGDB,"localSurf")
            print("     projecting input clip to WGS 1984 to match service...")
            arcpy.Project_management(inputPolygonFC,tempClipExtent,srWGS84)
            tempCellSize = CellSize(tempClipExtent)
            #MakeImageServerLayer_management (in_image_service, out_imageserver_layer, {template},
            #{band_index}, {mosaic_method}, {order_field},
            #{order_base_value}, {lock_rasterid}, {cell_size},
            #{where_clause}, {processing_template})
            print("     getting image service layer with cell size " + str(tempCellSize) + "...")
            arcpy.MakeImageServerLayer_management(inputSurface, "inputSurface", tempClipExtent,
                                                  "#", "#", "#",
                                                  "#", "#", tempCellSize)
            print("     projecting image service layer to match target data...")
            arcpy.ProjectRaster_management("inputSurface",localSurf,srWebMerc)
            #arcpy.CopyRaster_management("inputSurface", localSurf)
        except arcpy.ExecuteError:
            print("Error converting image service...")
            msgs = arcpy.GetMessages()
            print(msgs)
            sys.exit(-1)

        numberOfPeaks = 3

        ########################################################
        # Execute the Model under test:
        arcpy.FindLocalPeaks_MAoT(inputPolygonFC, numberOfPeaks, localSurf, outputPointsFC)
        ########################################################

        # Verify the results
        outputFeatureCount = int(arcpy.GetCount_management(outputPointsFC).getOutput(0)) 
        print("Output FeatureClass: " + str(outputPointsFC))
        print("Output Feature Count: " +  str(outputFeatureCount))

        if (outputPointsFC < 3):
            print("Invalid Output Feature Count: " +  str(outputFeatureCount))
            raise Exception("Test Failed")

        # WORKAROUND: delete scratch db
        print("Deleting Scratch Workspace (Workaround)")
        TestUtilities.deleteScratch()
        print("Test Successful")

    except arcpy.ExecuteError:
        # Get the tool error messages
        msgs = arcpy.GetMessages()
        arcpy.AddError(msgs)

        # return a system error code
        sys.exit(-1)

    except Exception as e:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]

        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

        # Return python error messages for use in script tool or Python Window
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)

        # return a system error code
        sys.exit(-1)

    finally:
        # Check in the 3D Analyst extension
        arcpy.CheckInExtension("Spatial")
        arcpy.CheckInExtension("3D")
        # if arcpy.Exists(localSurf):
        #     arcpy.Delete_management(localSurf)


RunTest()
