# coding: utf-8
'''
------------------------------------------------------------------------------
 Copyright 2017 Esri
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
------------------------------------------------------------------------------
 ==================================================
 GRGUtilities.py
 --------------------------------------------------
 requirements: ArcGIS X.X, Python 2.7 or Python 3.x
 author: ArcGIS Solutions
 contact: support@esri.com
 company: Esri
 ==================================================
 description:
 GRG objects module.
 ==================================================
 history:
 9/1/2017 - mf - original transfer from Clearing Ops tools
 ==================================================
'''


import os
import sys
import math
import traceback
import arcpy
from arcpy import env
from . import Utilities

DEBUG = True
appEnvironment = None

def labelFeatures(layer, field):
    ''' set up labeling for layer '''
    global appEnvironment
    if appEnvironment == "ARCGIS_PRO":
        if layer.supports("SHOWLABELS"):
            for lblclass in layer.listLabelClasses():
                lblclass.visible = True
                lblclass.expression = " [" + str(field) + "]"
            layer.showLabels = True
    elif appEnvironment == "ARCMAP":
        if layer.supports("LABELCLASSES"):
            for lblclass in layer.labelClasses:
                lblclass.showClassLabels = True
                lblclass.expression = " [" + str(field) + "]"
            layer.showLabels = True
            arcpy.RefreshActiveView()
    else:
        pass # if returns "OTHER"


def findLayerByName(layerName):
    '''  '''
    global mapList
    global mxd
    global appEnvironment
    #UPDATE
    if appEnvironment == "ARCGIS_PRO":
        for layer in mapList.listLayers():
            if layer.name == layerName:
                arcpy.AddMessage("Found matching layer [" + layer.name + "]")
                return layer
            else:
                arcpy.AddMessage("Incorrect layer: [" + layer.name + "]")
    #else: #Update for automated test
    elif appEnvironment == "ARCMAP":
        for layer in arcpy.mapping.ListLayers(mxd):
            if layer.name == layerName:
                arcpy.AddMessage("Found matching layer [" + layer.name + "]")
                return layer
            else:
                arcpy.AddMessage("Incorrect layer: [" + layer.name + "]")
    else:
        arcpy.AddWarning("Non-map environment")


def ColIdxToXlName_CanvasAreaGRG(index):
    ''' Converts an index into a letter, labeled like excel columns, A to Z, AA to ZZ, etc.'''
    ordA = ord('A')
    ordZ = ord('Z')
    len = ordZ - ordA + 1
    s = ""
    while(int(index) >= 0):
        s = chr(int(index) % len + ordA) + s
        index = math.floor(int(index) / len) - 1
    return s


def ColIdxToXlName_PointTargetGRG(index):
    ''' Converts an index into a letter, labeled like excel columns, A to Z, AA to ZZ, etc. '''
    if index < 1:
        raise ValueError("Index is too small")
    result = ""
    while True:
        if index > 26:
            index, r = divmod(index - 1, 26)
            result = chr(r + ord('A')) + result
        else:
            return chr(index + ord('A') - 1) + result


'''
Sample adapted/taken from: https://github.com/usgs/arcgis-sample/blob/master/scripts/RotateFeatureClass.py
License: Public Domain: https://github.com/usgs/arcgis-sample/blob/master/LICENSE.txt
'''
def RotateFeatureClass(inputFC, outputFC,
                       angle=0, pivot_point=None):
    """Rotate Feature Class

    inputFC     Input features
    outputFC    Output feature class
    angle       Angle to rotate, in degrees
    pivot_point X,Y coordinates (as space-separated string)
                Default is lower-left of inputFC

    As the output feature class no longer has a "real" xy locations,
    after rotation, it no coordinate system defined.
    """


    def RotateXY(x, y, xc=0, yc=0, angle=0, units="DEGREES"):
        """Rotate an xy cooordinate about a specified origin
        x,y      xy coordinates
        xc,yc   center of rotation
        angle   angle
        units    "DEGREES" (default) or "RADIANS"
        """
        x = x - xc
        y = y - yc
        # make angle clockwise (like Rotate_management)
        angle = angle * -1
        if units == "DEGREES":
            angle = math.radians(angle)
        xr = (x * math.cos(angle)) - (y * math.sin(angle)) + xc
        yr = (x * math.sin(angle)) + (y * math.cos(angle)) + yc
        return xr, yr

    # temp names for cleanup
    env_file = None
    lyrFC, lyrTmp = [None] * 2  # layers
    tmpFC  = None # temp dataset

    try:
        # process parameters
        try:
            xcen, ycen = [float(xy) for xy in pivot_point.split()]
            pivot_point = xcen, ycen
        except:
            # if pivot point was not specified, get it from
            # the lower-left corner of the feature class
            ext = arcpy.Describe(inputFC).extent
            xcen, ycen  = ext.XMin, ext.YMin
            pivot_point = xcen, ycen

        angle = float(angle)

        # set up environment
        env_file = arcpy.CreateScratchName("xxenv",".xml","file",
                                           os.environ["TEMP"])
        arcpy.gp.SaveSettings(env_file)

        WKS = env.workspace
        if not WKS:
            if os.path.dirname(outputFC):
                WKS = os.path.dirname(outputFC)
            else:
                WKS = os.path.dirname(
                    arcpy.Describe(inputFC).catalogPath)
        env.workspace = env.scratchWorkspace = WKS

        # Disable any GP environment clips
        arcpy.ClearEnvironment("extent")

        # get feature class properties
        lyrFC = 'lyrFC'
        arcpy.MakeFeatureLayer_management(inputFC, lyrFC)
        dFC = arcpy.Describe(lyrFC)
        shpField = dFC.shapeFieldName
        shpType = dFC.shapeType

        # create temp feature class
        tmpFC = arcpy.CreateScratchName("xxfc", "", "featureclass")

        # Create Feature Class using inputFC as template (so will have "Grid" field)
        arcpy.CreateFeatureclass_management(os.path.dirname(tmpFC),
                                            os.path.basename(tmpFC),
                                            shpType,
                                            inputFC)
        lyrTmp = 'lyrTmp'
        arcpy.MakeFeatureLayer_management(tmpFC, lyrTmp)

        ## WORKAROUND: removed below because it was creating a schema lock until Pro/arcpy exited
        ## set up grid field
        #gridField = "Grid"
        #arcpy.AddField_management(lyrTmp, gridField, "TEXT")
        #arcpy.DeleteField_management(lyrTmp, 'ID')

        # rotate the feature class coordinates for each feature, and each feature part

        # open read and write cursors
        updateFields = ['SHAPE@','Grid']
        arcpy.AddMessage('Rotating temporary dataset')

        parts = arcpy.Array()
        rings = arcpy.Array()
        ring = arcpy.Array()

        with arcpy.da.SearchCursor(lyrFC, updateFields) as inRows,\
          arcpy.da.InsertCursor(lyrTmp, updateFields) as outRows:
            for inRow in inRows:
                shp = inRow[0] # SHAPE
                p = 0
                for part in shp:
                    for pnt in part:
                        if pnt:
                            x, y = RotateXY(pnt.X, pnt.Y, xcen, ycen, angle)
                            ring.add(arcpy.Point(x, y, pnt.ID))
                        else:
                            # if we have a ring, save it
                            if len(ring) > 0:
                                rings.add(ring)
                                ring.removeAll()
                    # we have our last ring, add it
                    rings.add(ring)
                    ring.removeAll()
                    # if only one, remove nesting
                    if len(rings) == 1: rings = rings.getObject(0)
                    parts.add(rings)
                    rings.removeAll()
                    p += 1

                # if only one, remove nesting
                if len(parts) == 1: parts = parts.getObject(0)
                if dFC.shapeType == "Polyline":
                    shp = arcpy.Polyline(parts)
                else:
                    shp = arcpy.Polygon(parts)
                parts.removeAll()

                gridValue = inRow[1] # GRID string
                outRows.insertRow([shp, gridValue])  # write row to output

        arcpy.AddMessage('Merging temporary, rotated dataset with output')
        env.qualifiedFieldNames = False
        arcpy.Merge_management(lyrTmp, outputFC)

    except MsgError as xmsg:
        arcpy.AddError(str(xmsg))
    except arcpy.ExecuteError:
        tbinfo = traceback.format_tb(sys.exc_info()[2])[0]
        arcpy.AddError(tbinfo.strip())
        arcpy.AddError(arcpy.GetMessages())
        numMsg = arcpy.GetMessageCount()
        for i in range(0, numMsg):
            arcpy.AddReturnMessage(i)
    except Exception as xmsg:
        tbinfo = traceback.format_tb(sys.exc_info()[2])[0]
        arcpy.AddError(tbinfo + str(xmsg))
    finally:
        # reset environment
        if env_file: arcpy.gp.LoadSettings(env_file)
        # Clean up temp files
        for f in [lyrFC, lyrTmp, tmpFC, env_file]:
            try:
                if f and arcpy.Exists(f) :
                    arcpy.Delete_management(f)
            except:
                pass

        # return pivot point
        try:
            pivot_point = "{0} {1}".format(*pivot_point)
        except:
            pivot_point = None

        return pivot_point

    # END RotateFeatureClass

def GRGFromArea(AOI,
                cellWidth,
                cellHeight,
                cellUnits,
                labelStartPos,
                labelStyle,
                labelSeperator,
                outputFeatureClass):
    '''Create Gridded Reference Graphic (GRG) from area input.'''

    fishnet = os.path.join("in_memory", "fishnet")
    DEBUG = True
    # GLOBALS
    mxd = None
    df = None
    aprx = None
    mapList = None
    scratch = None
    fc_WM = None

    try:
        #UPDATE
        appEnvironment = Utilities.GetApplication()
        if DEBUG == True: arcpy.AddMessage("App environment: " + appEnvironment)

        fc = os.path.join("in_memory", "AOI")
        arcpy.CopyFeatures_management(AOI, fc)

        if appEnvironment == "ARCGIS_PRO":
            from arcpy import mp
            aprx = arcpy.mp.ArcGISProject("CURRENT")
            mapList = aprx.listMaps()[0]
        #else: #Update for automated test
        if appEnvironment == "ARCMAP":
            from arcpy import mapping
            mxd = arcpy.mapping.MapDocument('CURRENT')
            df = arcpy.mapping.ListDataFrames(mxd)[0]

        arcpy.env.overwriteOutput = True
        if arcpy.env.scratchWorkspace:
            scratch = arcpy.env.scratchWorkspace
        else:
            scratch = r"%scratchGDB%"

        #If AOI is not in WebMercator, re-project to it
        if arcpy.Describe(AOI).spatialReference.name != "WGS_1984_Web_Mercator_Auxiliary_Sphere":
            fc_WM = os.path.join(scratch, "AOI_WM")
            outCS = arcpy.SpatialReference(3857) #the code for WGS84 Web Mercator
            arcpy.Project_management(fc, fc_WM, outCS)
            fc = fc_WM

        # From the template extent, create a polygon that we can project into a localized World Azimuthal Equidistan
        if DEBUG == True: arcpy.AddMessage("Getting extent info...")

        '''
        ' If cell units are feet convert to meters
        '''
        if (cellUnits == "Feet"):
            cellWidth = float(cellWidth) / 3.2808
            cellHeight = float(cellHeight) / 3.2808

        '''
        ' If cell units are kilometers convert to meters
        '''
        if (cellUnits == "Kilometers"):
            cellWidth = float(cellWidth) * 1000
            cellHeight = float(cellHeight) * 1000

        '''
        ' If cell units are miles convert to meters
        '''
        if (cellUnits == "Miles"):
            cellWidth = float(cellWidth) * 1609.344
            cellHeight = float(cellHeight) * 1609.344

        '''
        ' If cell units are yards convert to meters
        '''
        if (cellUnits == "Yards"):
            cellWidth = float(cellWidth) * 0.9144
            cellHeight = float(cellHeight) * 0.9144

        '''
        ' If cell units are Nautical Miles convert to meters
        '''
        if (cellUnits == "Nautical Miles"):
            cellWidth = float(cellWidth) * 1852
            cellHeight = float(cellHeight) * 1852

        '''
        ' create a minimum bounding rectangle around the AOI
        ' The use of the MBG_FIELDS option in MinimumBoundingGeometry_management
        ' tool also creates a field that has the shape orientation
        '''
        arcpy.AddMessage("Getting Minimum Bounding Geometry that fits the Area of Interest")
        minBound = os.path.join("in_memory","minBound")
        arcpy.MinimumBoundingGeometry_management(fc, minBound, 'RECTANGLE_BY_AREA','#','#','MBG_FIELDS')

        '''
        ' Extract the minimum bounding rectangle orienatation angle to a variable
        '''
        for row in arcpy.da.SearchCursor(minBound,["MBG_Orientation","MBG_LENGTH","MBG_WIDTH"]):
            orientation = row[0]
            arcpy.AddMessage("Orientation Angle: {0}".format(str(orientation)))
            if(orientation >= 45 and orientation <= 135):
                horizontalCells = math.ceil(row[1]/float(cellWidth))
                verticalCells = math.ceil(row[2]/float(cellHeight))
            else:
                verticalCells = math.ceil(row[1]/float(cellWidth))
                horizontalCells = math.ceil(row[2]/float(cellHeight))
            arcpy.AddMessage('Creating Grid {0} x {1}'.format(horizontalCells,verticalCells))

        arcpy.AddMessage(labelStartPos)
        '''
        ' Set up labeling depending on start position
        '''
        labelNumber = 0
        letterIndex = 0
        secondLetterIndex = 0

        if labelStartPos == "Upper-Left":
            letterIndex = verticalCells - 1
            secondLetterIndex = -1
            if labelStyle != 'Numeric':
                labelNumber = 0
            else:
                labelNumber = (verticalCells - 1) * horizontalCells
        elif labelStartPos == "Upper-Right":
            letterIndex = verticalCells - 1
            secondLetterIndex = horizontalCells
            if labelStyle != 'Numeric':
                labelNumber = horizontalCells + 1
            else:
                labelNumber = (verticalCells * horizontalCells) + 1
        elif labelStartPos == "Lower-Right":
            letterIndex = 0
            secondLetterIndex = horizontalCells
            labelNumber = horizontalCells + 1
        elif labelStartPos == "Lower-Left":
            letterIndex = 0
            secondLetterIndex = -1
            labelNumber = 0

        '''
        ' Explode the minimum bounding rectangle to points
        '''
        with arcpy.da.SearchCursor(minBound, 'SHAPE@XY', explode_to_points=True) as cursor:
            pts = [r[0] for r in cursor][0:4]

        '''
        ' Because the fishnet tool always creates a non rotated fishnet before it applies
        ' its rotation we need to determine what the opposite point location would be if the
        ' minimum polygon was not rotated
        '''
        if orientation < 45:
            angle = math.radians(orientation)
            x = float(pts[2][0]) - float(pts[0][0])
            y = float(pts[2][1]) - float(pts[0][1])
            xr = (x * math.cos(angle)) - (y * math.sin(angle)) + float(pts[0][0])
            yr = (x * math.sin(angle)) + (y * math.cos(angle)) + float(pts[0][1])
            origin = str(pts[0][0]) + ' ' + str(pts[0][1])
            yaxis =  str(pts[1][0]) + ' ' + str(pts[1][1])
        elif orientation >= 45 and orientation <= 135:
            angle = math.radians((90 - orientation) * -1)
            x = float(pts[1][0]) - float(pts[3][0])
            y = float(pts[1][1]) - float(pts[3][1])
            xr = (x * math.cos(angle)) - (y * math.sin(angle)) + float(pts[3][0])
            yr = (x * math.sin(angle)) + (y * math.cos(angle)) + float(pts[3][1])
            origin = str(pts[3][0]) + ' ' + str(pts[3][1])
            yaxis =  str(pts[0][0]) + ' ' + str(pts[0][1])
        else:
            angle = math.radians((180 - orientation) * -1)
            x = float(pts[0][0]) - float(pts[2][0])
            y = float(pts[0][1]) - float(pts[2][1])
            xr = (x * math.cos(angle)) - (y * math.sin(angle)) + float(pts[2][0])
            yr = (x * math.sin(angle)) + (y * math.cos(angle)) + float(pts[2][1])
            origin = str(pts[2][0]) + ' ' + str(pts[2][1])
            yaxis =  str(pts[3][0]) + ' ' + str(pts[3][1])

        oppositeCorner = str(xr) + " " + str(yr)

        '''
        ' Now use the CreateFishnet_management tool to create the desired grid
        '''
        arcpy.AddMessage("Creating Fishnet Grid...")
        arcpy.CreateFishnet_management(fishnet, origin, yaxis, str(cellWidth), str(cellHeight), 0, 0, oppositeCorner, "NO_LABELS", fc, "POLYGON")

        '''
        ' Add a field which will be used to add the grid labels
        '''
        arcpy.AddMessage("Adding field for labeling the grid")
        gridField = "Grid"
        arcpy.AddField_management(fishnet, gridField, "TEXT")

        '''
        ' Loop through features and label
        '''

        with arcpy.da.UpdateCursor(fishnet, ['OID','Grid']) as cursor:
            verticalCount = 0
            horizontalCount = 0
            for row in cursor:
                if labelStartPos == "Lower-Left" or labelStartPos == 'Upper-Left':
                    labelNumber = labelNumber + 1
                    secondLetterIndex = secondLetterIndex + 1
                else:
                    labelNumber = labelNumber - 1
                    secondLetterIndex = secondLetterIndex - 1

                letter = ColIdxToXlName_CanvasAreaGRG(int(letterIndex))
                secondLetter = ColIdxToXlName_CanvasAreaGRG(int(secondLetterIndex))

                if (labelStyle == "Alpha-Numeric"):
                    row[1] = letter + str(int(labelNumber))
                elif (labelStyle == "Alpha-Alpha"):
                    row[1] = letter + labelSeperator + secondLetter
                elif (labelStyle == "Numeric"):
                    row[1] = labelNumber

                cursor.updateRow(row)

                horizontalCount = horizontalCount + 1

                if horizontalCount >= horizontalCells:
                    horizontalCount = 0
                    verticalCount = verticalCount + 1
                    if labelStartPos == "Upper-Left":
                        letterIndex = letterIndex - 1
                        secondLetterIndex = -1
                        if labelStyle != 'Numeric':
                            labelNumber = 0
                        else:
                            labelNumber = (verticalCells - (verticalCount + 1)) * horizontalCells
                    elif labelStartPos == "Upper-Right":
                        letterIndex = letterIndex - 1
                        secondLetterIndex = horizontalCells
                        if labelStyle != 'Numeric':
                            labelNumber = horizontalCells + 1
                    elif labelStartPos == "Lower-Right":
                        letterIndex = letterIndex + 1
                        secondLetterIndex = horizontalCells
                        if labelStyle != 'Numeric':
                            labelNumber = horizontalCells + 1
                        else:
                            labelNumber = ((verticalCount + 1) * horizontalCells) + 1
                    elif labelStartPos == "Lower-Left":
                        letterIndex = letterIndex + 1
                        secondLetterIndex = -1
                        if labelStyle != 'Numeric':
                            labelNumber = 0

        arcpy.CopyFeatures_management(fishnet, outputFeatureClass)
        arcpy.Delete_management(fishnet)

        # Get and label the output feature
        #TODO: Update once applying symbology in Pro is fixed.
        targetLayerName = os.path.basename(outputFeatureClass.value)

        if appEnvironment == "ARCGIS_PRO":
            arcpy.AddMessage("Do not apply symbology it will be done in the next task step")

        elif appEnvironment == "ARCMAP":
            arcpy.AddMessage("Non-map environment, skipping labeling based on best practices")
        else:
            arcpy.AddMessage("Non-map environment, skipping labeling...")

        return outputFeatureClass

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

    finally:
        try:
            if arcpy.Exists(os.path.join(scratch, "AOI_WM")):
                arcpy.Delete_management(fc_WM)
        except:
            pass

def GRGFromPoint(starting_point,
                 horizontal_cells,
                 vertical_cells,
                 cell_width,
                 cell_height,
                 cell_units,
                 label_start_position,
                 label_style,
                 labelSeperator,
                 gridAngle,
                 output_feature_class):
    ''' Create Gridded Reference Graphic (GRG) from point input.'''


    targetPointOrigin = starting_point
    numberCellsHo = horizontal_cells
    numberCellsVert = vertical_cells
    cellWidth = cell_width
    cellHeight = cell_height
    cellUnits = cell_units
    labelStartPos = label_start_position
    labelStyle = label_style
    rotation = gridAngle
    outputFeatureClass = output_feature_class

    tempOutput = os.path.join("in_memory", "tempFishnetGrid")
    DEBUG = True
    mxd = None
    df, aprx = None, None
    point_WM = None
    scratch = None

    try:
        #UPDATE
        appEnvironment = Utilities.GetApplication()
        if DEBUG == True: arcpy.AddMessage("App environment: " + appEnvironment)

        if appEnvironment == "ARCGIS_PRO":
            from arcpy import mp
            aprx = arcpy.mp.ArcGISProject("CURRENT")
            mapList = aprx.listMaps()[0]
        elif appEnvironment == "ARCMAP":
            from arcpy import mapping
            mxd = arcpy.mapping.MapDocument('CURRENT')
            df = arcpy.mapping.ListDataFrames(mxd)[0]
        else:
            if DEBUG == True: arcpy.AddMessage("Non-map application...")

        numberOfFeatures = arcpy.GetCount_management(targetPointOrigin)
        if(int(numberOfFeatures[0]) == 0):
            raise Exception("The input start location must contain at least one feature.")

        if(int(numberOfFeatures[0]) > 1):
            arcpy.AddMessage("More than one feature detected for the start location, last feature entered will be used.")

        arcpy.env.overwriteOutput = True
        if arcpy.env.scratchWorkspace:
            scratch = arcpy.env.scratchWorkspace
        else:
            scratch = r"%scratchGDB%"

        #If starting point is not in WebMercator, re-project to it
        if arcpy.Describe(targetPointOrigin).spatialReference.name != "WGS_1984_Web_Mercator_Auxiliary_Sphere":
            point_WM = os.path.join(scratch, "GRG_POINT_WM")
            outCS = arcpy.SpatialReference(3857) #the code for WGS84 Web Mercator
            arcpy.Project_management(targetPointOrigin, point_WM, outCS)
            targetPointOrigin = point_WM
            arcpy.AddMessage("Projected starting point to Web Mercator.")

        '''
        ' If cell units are feet convert to meters
        '''
        if (cellUnits == "Feet"):
            cellWidth = float(cellWidth) / 3.2808
            cellHeight = float(cellHeight) / 3.2808

        '''
        ' If cell units are kilometers convert to meters
        '''
        if (cellUnits == "Kilometers"):
            cellWidth = float(cellWidth) * 1000
            cellHeight = float(cellHeight) * 1000

        '''
        ' If cell units are miles convert to meters
        '''
        if (cellUnits == "Miles"):
            cellWidth = float(cellWidth) * 1609.344
            cellHeight = float(cellHeight) * 1609.344

        '''
        ' If cell units are yards convert to meters
        '''
        if (cellUnits == "Yards"):
            cellWidth = float(cellWidth) * 0.9144
            cellHeight = float(cellHeight) * 0.9144

        '''
        ' If cell units are Nautical Miles convert to meters
        '''
        if (cellUnits == "Nautical Miles"):
            cellWidth = float(cellWidth) * 1852
            cellHeight = float(cellHeight) * 1852


        # Get the coordinates of the point inputExtentDrawnFromMap.
        rows = arcpy.SearchCursor(targetPointOrigin)
        extent = None
        for row in rows:
            shape = row.getValue("SHAPE")
            extent = shape.extent
        pointExtents = str.split(str(extent))

        ''' This seemed to be shifting the grid when it was not required so commented out

        # Shift the grid center point if the rows and/or columns are even.
        if (float(numberCellsHo)%2 == 0.0):
            hoShiftAmt = float(cellHeight) / 2.0

            # Determines shift up/down based on where box was inputExtentDrawnFromMap
            if inputExtentDrawnFromMap == False:
                pointExtents[1] = str(float(pointExtents[1]) - hoShiftAmt)
            elif (float(topLeftDrawn[1]) > float(pointExtents[1])):
                pointExtents[1] = str(float(pointExtents[1]) - hoShiftAmt)
            else:
                pointExtents[1] = str(float(pointExtents[1]) + hoShiftAmt)

        if (float(numberCellsVert)%2 == 0.0):
            vertShiftAmt = float(cellWidth) / 2.0

            # Determines shift left/right based on where box was inputExtentDrawnFromMap
            if inputExtentDrawnFromMap == False:
                pointExtents[0] = str(float(pointExtents[0]) - vertShiftAmt)
            elif (float(topLeftDrawn[0]) > float(pointExtents[0])):
                pointExtents[0] = str(float(pointExtents[0]) - vertShiftAmt)
            else:
                pointExtents[0] = str(float(pointExtents[0]) + vertShiftAmt)

        '''

        # From the template extent, get the origin, y axis, and opposite corner coordinates
        rightCorner =  float(pointExtents[0]) + ((float(cellWidth) * float(numberCellsVert)) /2.0)
        leftCorner = float(pointExtents[0]) - ((float(cellWidth) * float(numberCellsVert)) /2.0)
        topCorner = float(pointExtents[1]) + ((float(cellHeight) * float(numberCellsHo)) /2.0)
        bottomCorner = float(pointExtents[1]) - ((float(cellHeight) * float(numberCellsHo)) /2.0)
        originCoordinate = str(leftCorner) + " " + str(bottomCorner)
        yAxisCoordinate = str(leftCorner) + " " + str(bottomCorner + 10)
        oppCornerCoordinate = str(rightCorner) + " " + str(topCorner)
        fullExtent = str(leftCorner) + " " + str(bottomCorner) + " " + str(rightCorner) + " " + str(topCorner)

        # Set the start position for labeling
        startPos = None
        if (labelStartPos == "Upper-Right"):
            startPos = "UR"
        elif (labelStartPos == "Upper-Left"):
            startPos = "UL"
        elif (labelStartPos == "Lower-Left"):
            startPos = "LL"
        elif (labelStartPos == "Lower-Right"):
            startPos = "LR"

        arcpy.AddMessage("Creating Fishnet Grid")
        env.outputCoordinateSystem = arcpy.Describe(targetPointOrigin).spatialReference

        arcpy.CreateFishnet_management(tempOutput, originCoordinate, yAxisCoordinate, 0, 0, str(numberCellsHo), str(numberCellsVert), oppCornerCoordinate, "NO_LABELS", fullExtent, "POLYGON")

        # Sort the grid upper left to lower right, and delete the in memory one
        arcpy.AddMessage("Sorting the grid for labeling")
        tempSort = os.path.join("in_memory", "tempSort")
        arcpy.Sort_management(tempOutput, tempSort, [["Shape", "ASCENDING"]], startPos)
        # arcpy.Delete_management("in_memory") #Not sure why we are trying to delete in_memory

        # Add a field which will be used to add the grid labels
        arcpy.AddMessage("Adding field for labeling the grid")
        gridField = "Grid"
        arcpy.AddField_management(tempSort, gridField, "TEXT")

        # Number the fields
        arcpy.AddMessage("Numbering the grids")
        letterIndex = 1
        secondLetterIndex = 1
        letter = 'A'
        secondLetter = 'A'
        number = 1
        lastY = -9999
        cursor = arcpy.UpdateCursor(tempSort)
        for row in cursor:
            yPoint = row.getValue("SHAPE").firstPoint.Y
            if (lastY != yPoint) and (lastY != -9999):
                letterIndex += 1
                letter = ColIdxToXlName_PointTargetGRG(letterIndex)
                if (labelStyle != "Numeric"):
                    number = 1
                secondLetter = 'A'
                secondLetterIndex = 1
            lastY = yPoint

            if (labelStyle == "Alpha-Numeric"):
                row.setValue(gridField, str(letter) + str(number))
            elif (labelStyle == "Alpha-Alpha"):
                row.setValue(gridField, str(letter) + labelSeperator + str(secondLetter))
            elif (labelStyle == "Numeric"):
                row.setValue(gridField, str(number))

            cursor.updateRow(row)
            number += 1
            secondLetterIndex += 1
            secondLetter = ColIdxToXlName_PointTargetGRG(secondLetterIndex)

        # Rotate the shape, if needed.
        if (rotation != 0):
            arcpy.AddMessage("Rotating the grid")
            RotateFeatureClass(tempSort, outputFeatureClass, rotation, pointExtents[0] + " " + pointExtents[1])
        else:
            arcpy.CopyFeatures_management(tempSort, outputFeatureClass)
        arcpy.Delete_management(tempSort)

        # Get and label the output feature
        #UPDATE
        targetLayerName = os.path.basename(outputFeatureClass)
        if appEnvironment == "ARCGIS_PRO":
            arcpy.AddMessage("Do not apply symbology it will be done in the next task step")
        elif appEnvironment == "ARCMAP":
            arcpy.AddMessage("Non-map environment, skipping labeling based on best practices")
        else:
            arcpy.AddMessage("Non-map environment, skipping labeling...")

        return outputFeatureClass

    except arcpy.ExecuteError:
        # Get the tool error messages
        msgs = arcpy.GetMessages()
        arcpy.AddError(msgs)
        print(msgs)

    except Exception as xmsg:
        arcpy.AddError(str(xmsg))

    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]

        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + \
                "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

        # Return python error messages for use in script tool or Python Window
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)
        # Print Python error messages for use in Python / Python Window
        print(pymsg + "\n")
        print(msgs)

    finally:
        try:
            if arcpy.Exists(os.path.join(scratch, "GRG_POINT_WM")):
                arcpy.Delete_management(point_WM)
        except:
            pass

def NumberFeatures(areaToNumber,
                    pointFeatures,
                    numberingField,
                    outputFeatureClass):

        descPointFeatures = arcpy.Describe(pointFeatures)
        arcpy.AddMessage("pointFeatures: {0}".format(descPointFeatures.catalogPath))

        # If no output FC is specified, then set it a temporary one, as this will be copied to the input and then deleted.
        overwriteFC = False
        if not outputFeatureClass:
            DEFAULT_OUTPUT_LOCATION = r'%scratchGDB%\tempSortedPoints'
            outputFeatureClass = DEFAULT_OUTPUT_LOCATION
            overwriteFC = True
        else:
            descOutputFeatureClass = arcpy.Describe(outputFeatureClass)
            arcpy.AddMessage("outputFeatureClass: {0}".format(descOutputFeatureClass.catalogPath))

        # Sort layer by upper right across and then down spatially
        areaToNumberInMemory = os.path.join("in_memory","areaToNumber")
        arcpy.CopyFeatures_management(areaToNumber, areaToNumberInMemory)
        areaToNumber = areaToNumberInMemory

        DEBUG = True
        appEnvironment = None
        mxd, df, aprx, mp, mapList = None, None, None, None, None
        pointFeatureName = os.path.basename(str(pointFeatures))
        layerExists = False
        try:
            # Check that area to number is a polygon
            descArea = arcpy.Describe(areaToNumber)
            areaGeom = descArea.shapeType
            arcpy.AddMessage("Shape type: " + str(areaGeom))
            if (descArea.shapeType != "Polygon"):
                raise Exception("ERROR: The area to number must be a polygon.")

            #Checking the version of the Desktop Application
            appEnvironment = Utilities.GetApplication()
            if DEBUG == True: arcpy.AddMessage("App environment: " + appEnvironment)

            #Getting the layer name from the Table of Contents
            if appEnvironment == Utilities.PLATFORM_PRO:
                from arcpy import mp
                aprx = arcpy.mp.ArcGISProject("CURRENT")
                mapList = aprx.listMaps()[0]
                for lyr in mapList.listLayers():
                    if lyr.name == pointFeatureName:
                        layerExists = True
            #else:
            if appEnvironment == Utilities.PLATFORM_DESKTOP:
                from arcpy import mapping
                mxd = arcpy.mapping.MapDocument('CURRENT')
                df = arcpy.mapping.ListDataFrames(mxd)[0]
                for lyr in arcpy.mapping.ListLayers(mxd):
                    if lyr.name == pointFeatureName:
                        layerExists = True

            if layerExists == False:
                arcpy.MakeFeatureLayer_management(pointFeatures, pointFeatureName)
            else:
                pointFeatureName = pointFeatures

            # Select all the points that are inside of area
            if areaToNumber:
                arcpy.AddMessage("Selecting points from {0} inside of the area {1}".format(pointFeatureName, areaToNumber))
            else:
                arcpy.AddMessage("Selecting points from {0} inside of the area {1}".format(pointFeatureName, areaToNumber.name))

            selectionLayer = arcpy.SelectLayerByLocation_management(pointFeatureName, "INTERSECT",
                                                                    areaToNumber, "#", "NEW_SELECTION")
            if DEBUG == True:
                arcpy.AddMessage("Selected " + str(arcpy.GetCount_management(pointFeatureName).getOutput(0)) + " points")

            arcpy.AddMessage("Sorting the selected points geographically, left to right, top to bottom")
            arcpy.Sort_management(pointFeatureName, outputFeatureClass, [["Shape", "ASCENDING"]])

            #global numberingField
            if numberingField is None or numberingField == "":
                fnames = [field.name for field in arcpy.ListFields(outputFeatureClass)]
                addfield = "Number"
                if addfield in fnames:
                    arcpy.AddMessage("Number field is already used")
                    numberingField = "Number"
                else:
                    arcpy.AddMessage("Add One")
                    arcpy.AddMessage("Adding Number field because no input field was given")
                    arcpy.AddField_management(outputFeatureClass,"Number","SHORT")
                    numberingField = "Number"
            else:
                pass

            # Number the fields
            arcpy.AddMessage("Numbering the fields")
            i = 1
            cursor = arcpy.UpdateCursor(outputFeatureClass) # Object: Error in parsing arguments for UpdateCursor
            for row in cursor:
                row.setValue(numberingField, i)
                cursor.updateRow(row)
                i += 1
            # Clear the selection
            arcpy.AddMessage("Clearing the selection")
            arcpy.SelectLayerByAttribute_management(pointFeatureName, "CLEAR_SELECTION")

            # Overwrite the Input Point Features, and then delete the temporary output feature class
            targetLayerName = ""
            if (overwriteFC):
                arcpy.AddMessage("Copying the features to the input, and then deleting the temporary feature class")
                desc = arcpy.Describe(pointFeatures)
                if hasattr(desc, "layer"):
                    overwriteFC = desc.layer.catalogPath
                else:
                    overwriteFC = desc.catalogPath

                arcpy.AddMessage("what is the numberingField: " + str(numberingField))
                addfield = "Number"
                fnames1 = [field.name for field in arcpy.ListFields(overwriteFC)]
                if addfield in fnames1:
                    arcpy.AddMessage("Number field is already used")
                else:
                    arcpy.AddMessage("Adding Number field to overwriteFC due to no input field")
                    arcpy.AddField_management(overwriteFC,"Number")
                    arcpy.AddMessage("Added Number field to overwriteFC")

                fields = (str(numberingField), "SHAPE@")

                overwriteCursor = arcpy.da.UpdateCursor(overwriteFC, fields)
                for overwriteRow in overwriteCursor:
                    sortedPointsCursor = arcpy.da.SearchCursor(outputFeatureClass, fields)
                    for sortedRow in sortedPointsCursor:
                        if sortedRow[1].equals(overwriteRow[1]):
                            overwriteRow[0] = sortedRow[0]
                    overwriteCursor.updateRow(overwriteRow)
                arcpy.Delete_management(outputFeatureClass)
                targetLayerName = pointFeatureName
            else:
                targetLayerName = os.path.basename(str(outputFeatureClass))

            # Workaround: don't set the outputFeatureClass if none was supplied to the tool
            if overwriteFC:
                outputFeatureClass = ''

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

        return outputFeatureClass
