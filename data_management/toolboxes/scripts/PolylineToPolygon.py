#------------------------------------------------------------------------------
# Copyright 2014 Esri
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

# Polyline To Polygon
import os, sys
import arcpy, traceback
from arcpy import env

inputPolylines = arcpy.GetParameterAsText(0)
inputIDFieldName = arcpy.GetParameterAsText(1)
outputPolygons = arcpy.GetParameterAsText(2)
delete_me = []
debug = False

try:
    currentOverwriteOutput = env.overwriteOutput
    env.overwriteOutput = True

    #Create output Poly FC
    sr = arcpy.Describe(inputPolylines).spatialReference
    arcpy.AddMessage("Spatial reference is " + str(sr))
    arcpy.AddMessage("Creating output feature class...")
    outpolygonsFC = arcpy.CreateFeatureclass_management(os.path.dirname(outputPolygons),os.path.basename(outputPolygons),"POLYGON","#","#","#",sr)

    #Add ID field
    arcpy.AddMessage("Adding ID field ...")
    arcpy.AddField_management(outpolygonsFC,inputIDFieldName,"LONG")
    arcpy.AddMessage("Opening cursors ...")

    #Open Search cursor on polyline
    inFields = ["SHAPE@", inputIDFieldName]
    inRows = arcpy.da.SearchCursor(inputPolylines, inFields)

    #Open Insert cursor on polygons
    outRows = arcpy.da.InsertCursor(outpolygonsFC,inFields)

    for row in inRows:
        feat = row[0]
        inID = row[1]

        arcpy.AddMessage("Building points from lines.")
        #Build array of points for the line
        polyArray = arcpy.Array()
        partnum = 0
        for part in feat:
            for pnt in feat.getPart(partnum):
                polyArray.add(arcpy.Point(pnt.X, pnt.Y))
            partnum += 1

        arcpy.AddMessage("Creating polygon from points.")
        #convert the array to a polygon, and insert the features
        outPoly = arcpy.Polygon(polyArray)
        outRows.insertRow([outPoly, inID])

    #close cursors
    del outRows
    del inRows

    #set outputs
    arcpy.SetParameter(2,outpolygonsFC)

    # cleanup
    arcpy.AddMessage("Removing scratch datasets:")
    for ds in delete_me:
       arcpy.AddMessage(str(ds))
       arcpy.Delete_management(ds)

    env.overwriteOutput = currentOverwriteOutput

except arcpy.ExecuteError:
    error = True
    # Get the tool error messages
    msgs = arcpy.GetMessages()
    arcpy.AddError(msgs)
    #print msgs #UPDATE
    print(msgs)

except:
    # Get the traceback object
    error = True
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    # Return python error messages for use in script tool or Python Window
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)

    # Print Python error messages for use in Python / Python Window
    #print pymsg + "\n" #UPDATE
    print(pymsg + "\n")
    #print msgs #UPDATE
    print(msgs)
