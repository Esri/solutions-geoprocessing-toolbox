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
    lyrFC, lyrTmp, lyrOut   = [None] * 3  # layers
    tmpFC  = None # temp dataset
    Row, Rows, oRow, oRows = [None] * 4 # cursors

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
        arcpy.SaveSettings(env_file)

        # Disable any GP environment clips or project on the fly
        arcpy.ClearEnvironment("extent")
        arcpy.ClearEnvironment("outputCoordinateSystem")
        WKS = env.workspace
        if not WKS:
            if os.path.dirname(outputFC):
                WKS = os.path.dirname(outputFC)
            else:
                WKS = os.path.dirname(
                    arcpy.Describe(inputFC).catalogPath)
        env.workspace = env.scratchWorkspace = WKS

        # Disable GP environment clips or project on the fly
        arcpy.ClearEnvironment("extent")
        arcpy.ClearEnvironment("outputCoordinateSystem")

        # get feature class properties
        lyrFC = 'lyrFC'
        arcpy.MakeFeatureLayer_management(inputFC, lyrFC)
        dFC = arcpy.Describe(lyrFC)
        shpField = dFC.shapeFieldName
        shpType = dFC.shapeType
        FID = dFC.OIDFieldName

        # create temp feature class
        tmpFC = arcpy.CreateScratchName("xxfc", "", "featureclass")
        arcpy.CreateFeatureclass_management(os.path.dirname(tmpFC),
                                            os.path.basename(tmpFC),
                                            shpType)
        lyrTmp = 'lyrTmp'
        arcpy.MakeFeatureLayer_management(tmpFC, lyrTmp)

        # set up id field (used to join later)
        TFID = "XXXX_FID"
        arcpy.AddField_management(lyrTmp, TFID, "LONG")
        arcpy.DeleteField_management(lyrTmp, 'ID')

        # rotate the feature class coordinates
        # only points, polylines, and polygons are supported

        # open read and write cursors
        Rows = arcpy.SearchCursor(lyrFC, "", "",
                                  "%s;%s" % (shpField,FID))
        oRows = arcpy.InsertCursor(lyrTmp)
        arcpy.AddMessage("Opened search cursor")
        if shpType  == "Point":
            for Row in Rows:
                shp = Row.getValue(shpField)
                pnt = shp.getPart()
                pnt.X, pnt.Y = RotateXY(pnt.X, pnt.Y, xcen, ycen, angle)
                oRow = oRows.newRow()
                oRow.setValue(shpField, pnt)
                oRow.setValue(TFID, Row. getValue(FID))
                oRows.insertRow(oRow)
        elif shpType in ["Polyline", "Polygon"]:
            parts = arcpy.Array()
            rings = arcpy.Array()
            ring = arcpy.Array()
            for Row in Rows:
                shp = Row.getValue(shpField)
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
                oRow = oRows.newRow()
                oRow.setValue(shpField, shp)
                oRow.setValue(TFID,Row.getValue(FID))
                oRows.insertRow(oRow)
        else:
            raise Exception("Shape type {0} is not supported".format(shpType))

        del oRow, oRows # close write cursor (ensure buffer written)
        oRow, oRows = None, None # restore variables for cleanup

        # join attributes, and copy to output
        arcpy.AddJoin_management(lyrTmp, TFID, lyrFC, FID)
        env.qualifiedFieldNames = False
        arcpy.Merge_management(lyrTmp, outputFC)
        lyrOut = 'lyrOut'
        arcpy.MakeFeatureLayer_management(outputFC, lyrOut)
        # drop temp fields 2,3 (TFID, FID)
        fnames = [f.name for f in arcpy.ListFields(lyrOut)]
        dropList = ';'.join(fnames[2:4])
        arcpy.DeleteField_management(lyrOut, dropList)

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
        if env_file: arcpy.LoadSettings(env_file)
        # Clean up temp files
        for f in [lyrFC, lyrTmp, lyrOut, tmpFC, env_file]:
            try:
                if f: arcpy.Delete_management(f)
            except:
                pass
        # delete cursors
        try:
            for c in [Row, Rows, oRow, oRows]: del c
        except:
            pass

        # return pivot point
        try:
            pivot_point = "{0} {1}".format(*pivot_point)
        except:
            pivot_point = None

        return pivot_point


def GRGFromArea(AOI,
                cellWidth,
                cellHeight,
                cellUnits,
                labelStartPos,
                labelStyle,
                outputFeatureClass):
    '''Create Gridded Reference Graphic (GRG) from area input.'''

    fishnet = os.path.join("in_memory", "fishnet")
    DEBUG = True
    # GLOBALS
    mxd = None
    df = None
    aprx = None
    mapList = None

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

        # From the template extent, create a polygon that we can project into a localized World Azimuthal Equidistan
        if DEBUG == True: arcpy.AddMessage("Getting extent info...")

        '''
        ' If cell units are feet convert to meters
        '''
        if (cellUnits == "Feet"):
            cellWidth = float(cellWidth) / 3.2808
            cellHeight = float(cellHeight) / 3.2808

        '''
        ' create a minimum bounding rectangle around the AOI
        ' The use of the MBG_FIELDS option in MinimumBoundingGeometry_management 
        ' tool also creates a field that has the shape orientation
        '''
        arcpy.AddMessage("Getting Minimum Bounding Geometry that fits the Area of Interest")
        minBound = os.path.join("in_memory","minBound")
        arcpy.MinimumBoundingGeometry_management(fc, minBound, 'RECTANGLE_BY_WIDTH','#','#','MBG_FIELDS')

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
                    row[1] = letter + secondLetter
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

        # Set tool output
        arcpy.SetParameter(6, outputFeatureClass)

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


def GRGFromPoint(starting_point,
                 horizontal_cells,
                 vertical_cells,
                 cell_width,
                 cell_height,
                 cell_units,
                 grid_size_feature_set,
                 label_start_position,
                 label_style,
                 output_feature_class):
    ''' Create Gridded Reference Graphic (GRG) from point input.'''

    targetPointOrigin = starting_point #arcpy.GetParameterAsText(0)
    numberCellsHo = horizontal_cells #arcpy.GetParameterAsText(1)
    numberCellsVert = vertical_cells #arcpy.GetParameterAsText(2)
    cellWidth = cell_width #arcpy.GetParameterAsText(3)
    cellHeight = cell_height #arcpy.GetParameterAsText(4)
    cellUnits = cell_units #arcpy.GetParameterAsText(5)
    gridSize = grid_size_feature_set #arcpy.GetParameterAsText(6)
    labelStartPos = label_start_position #arcpy.GetParameterAsText(7)
    labelStyle = label_style #arcpy.GetParameterAsText(8)
    outputFeatureClass = output_feature_class #arcpy.GetParameterAsText(9)
    tempOutput = os.path.join("in_memory", "tempFishnetGrid")
    DEBUG = True
    mxd = None
    df, aprx = None, None


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

        # If grid size is drawn on the map, use this instead of cell width and cell height
        inputExtentDrawnFromMap = False
        angleDrawn = 0
        workspace = arcpy.env.workspace
        topLeftDrawn = 0
        if float(cellWidth) == 0 and float(cellHeight) == 0:
            inputExtentDrawnFromMap = True
            tempGridFC = os.path.join(arcpy.env.scratchWorkspace, "GridSize")
            arcpy.CopyFeatures_management(gridSize, tempGridFC)
            pts = None
            with arcpy.da.SearchCursor(tempGridFC, 'SHAPE@XY', explode_to_points=True) as cursor:
                pts = [r[0] for r in cursor][0:4]
            arcpy.Delete_management(tempGridFC)

            # Find the highest points in the drawn rectangle, to calculate the top left and top right coordinates.
            highestPoint = None
            nextHighestPoint = None
            for pt in pts:
                if highestPoint is None or pt[1] > highestPoint[1]:
                    nextHighestPoint = highestPoint
                    highestPoint = pt
                elif nextHighestPoint is None or pt[1] > nextHighestPoint[1]:
                    nextHighestPoint = pt

            topLeft = highestPoint if highestPoint[0] < nextHighestPoint[0] else nextHighestPoint
            topRight = highestPoint if highestPoint[0] > nextHighestPoint[0] else nextHighestPoint
            topLeftDrawn = topLeft

            # Calculate the cell height and cell width
            cellWidth= math.sqrt((pts[0][0] - pts[1][0]) ** 2 + (pts[0][1] - pts[1][1]) ** 2)
            cellHeight = math.sqrt((pts[1][0] - pts[2][0]) ** 2 + (pts[1][1] - pts[2][1]) ** 2)

            # Calculate angle
            hypotenuse = math.sqrt(math.pow(topLeft[0] - topRight[0], 2) + math.pow(topLeft[1] - topRight[1], 2))
            adjacent = topRight[0] - topLeft[0]
            numberToCos = float(adjacent)/float(hypotenuse)
            angleInRadians = math.acos(numberToCos)
            angleDrawn = math.degrees(angleInRadians)
            if (topRight[1] > topLeft[1]):
                angleDrawn = 360 - angleDrawn
        else:
            if (cellUnits == "Feet"):
                cellWidth = float(cellWidth) * 0.3048
                cellHeight = float(cellHeight) * 0.3048

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

        # If grid size is drawn on the map, then calculate the rotation of the grid
        if inputExtentDrawnFromMap:
            # Find the highest two points in the inputExtentDrawnFromMap shape
            highestPoint = None
            nextHighestPoint = None
            for pt in pts:
                if highestPoint is None or pt[1] > highestPoint[1]:
                    nextHighestPoint = highestPoint
                    highestPoint = pt
                elif nextHighestPoint is None or pt[1] > nextHighestPoint[1]:
                    nextHighestPoint = pt
            topLeft = highestPoint if highestPoint[0] < nextHighestPoint[0] else nextHighestPoint
            topRight = highestPoint if highestPoint[0] > nextHighestPoint[0] else nextHighestPoint
            yDiff = topRight[1] - topLeft[1]
            xDiff = topRight[0] - topLeft[0]

            # Set the Y-Axis Coordinate so that the grid rotates properly
            extentHeight = float(topCorner) - float(bottomCorner)

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
                row.setValue(gridField, str(letter) + str(secondLetter))
            elif (labelStyle == "Numeric"):
                row.setValue(gridField, str(number))

            cursor.updateRow(row)
            number += 1
            secondLetterIndex += 1
            secondLetter = ColIdxToXlName_PointTargetGRG(secondLetterIndex)

        # Rotate the shape, if needed.
        if (inputExtentDrawnFromMap):
            arcpy.AddMessage("Rotating the grid")
            RotateFeatureClass(tempSort, outputFeatureClass, angleDrawn, pointExtents[0] + " " + pointExtents[1])
        else:
            arcpy.CopyFeatures_management(tempSort, outputFeatureClass)
        arcpy.Delete_management(tempSort)

        # Get and label the output feature
        #UPDATE
        targetLayerName = os.path.basename(outputFeatureClass.value)
        if appEnvironment == "ARCGIS_PRO":
            arcpy.AddMessage("Do not apply symbology it will be done in the next task step")
        elif appEnvironment == "ARCMAP":
            arcpy.AddMessage("Non-map environment, skipping labeling based on best practices")
        else:
            arcpy.AddMessage("Non-map environment, skipping labeling...")

        # Set tool output
        arcpy.SetParameter(8, outputFeatureClass)

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
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + \
                "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

        # Return python error messages for use in script tool or Python Window
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)
        # Print Python error messages for use in Python / Python Window
        print(pymsg + "\n")
        print(msgs)

    return outputFeatureClass
