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

# LOCALS ===========================================

debug = True # extra messaging during development

# FUNCTIONS ========================================

def polylineToPolygon(inputPolylines, inputIDFieldName, outputPolygons):
    '''
    Converts polyline to polygon features. All closed features will
    be converted to polygons. Unclosed polylines, or polylines with
    less than 2 vertices will not convert.
    
    inputPolylines - input polyline feature class
    idFieldName - field in inputPolylines to separate individual features
    outputPolygons - polygon feature class to be created
    
    returns polygon feature class
    '''
    try:
        env.overwriteOutput = True
        #Create output Poly FC
        sr = arcpy.Describe(inputPolylines).spatialReference
        # if debug:
        #     arcpy.AddMessage("Spatial reference is " + str(sr.name))
        #     arcpy.AddMessage("Creating output feature class...")
        outpolygonsFC = arcpy.CreateFeatureclass_management(os.path.dirname(outputPolygons),  \
                                                            os.path.basename(outputPolygons), \
                                                            "POLYGON", \
                                                            "#", \
                                                            "#", \
                                                            "#", \
                                                            sr)
        
        inFields = ["SHAPE@"]
        if inputIDFieldName:
            #Add ID field
            if debug:
                arcpy.AddMessage("Adding ID field: %s ..." % str(inputIDFieldName))
            arcpy.AddField_management(outpolygonsFC,inputIDFieldName, "LONG")
            inFields = ["SHAPE@", inputIDFieldName]

        if debug:
            arcpy.AddMessage("Converting Polylines to Polygons...")

        #Open Search cursor on polyline
        inRows = arcpy.da.SearchCursor(inputPolylines, inFields)
    
        #Open Insert cursor on polygons
        outRows = arcpy.da.InsertCursor(outpolygonsFC, inFields)
    
        polyArray = arcpy.Array()

        rowCount = 0

        for row in inRows:

            rowCount += 1

            # Provide feedback, since this method may take a while for large datasets
            if debug and not (rowCount % 100):
                arcpy.AddMessage('Processing Row: ' + str(rowCount))

            if inputIDFieldName:
                inID = row[1]

            # Polyline will only have one part
            featShape = row[0]
            polyline = featShape.getPart(0)

            polyArray.removeAll()
            polyArray.append(polyline)

            outPoly = arcpy.Polygon(polyArray, sr)

            if inputIDFieldName:
                outRows.insertRow([outPoly, inID])
            else:
                outRows.insertRow([outPoly])

        if debug:
            arcpy.AddMessage("Done converting polylines to polygons ...")
                
        #close cursors
        del outRows
        del inRows
        return outputPolygons
    
    except arcpy.ExecuteError:
        # Get the tool error messages
        msgs = arcpy.GetMessages()
        arcpy.AddError(msgs)
        print(msgs)

    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]

        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

        # Return python error messages for use in script tool or Python Window
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)

        # Print Python error messages for use in Python / Python Window
        print(pymsg + "\n")
        print(msgs)

def main():

    inputPolylines = arcpy.GetParameterAsText(0)
    inputIDFieldName = arcpy.GetParameterAsText(1)
    outputPolygons = arcpy.GetParameterAsText(2)

    #Polyline To Polygon
    polylineToPolygon(inputPolylines, inputIDFieldName, outputPolygons)

if __name__ == "__main__":
    main()
