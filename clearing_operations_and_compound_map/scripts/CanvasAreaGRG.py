# coding: utf-8
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
#
# ==================================================
# CanvasAreaGRG.py
# --------------------------------------------------
# Built on ArcGIS 10.?
# ==================================================
#
# Creates a Gridded Reference Graphic
#
#
# ==================================================
# HISTORY:
#
# 7/21/2017 - ag -  Rewrite of tool to support other projections
#                   Fix grid not covering AOI when rotated
#                   Use the out of the box fishnet tool
# 8/24/2015 - mf -  Needed to update script for non-ArcMap/Pro testing environment
#
# ==================================================

import os, sys, math, traceback, inspect
import arcpy
from arcpy import env
import Utilities

# Read in the parameters
AOI = arcpy.GetParameterAsText(0)
cellWidth = arcpy.GetParameterAsText(1)
cellHeight = arcpy.GetParameterAsText(2)
cellUnits = arcpy.GetParameterAsText(3)
labelStartPos = arcpy.GetParameterAsText(4)
labelStyle = arcpy.GetParameterAsText(5)
outputFeatureClass = arcpy.GetParameterAsText(6)

fishnet = os.path.join("in_memory", "fishnet")

DEBUG = True
# GLOBALS
appEnvironment = None
mxd = None
df = None
aprx = None
mapList = None

def labelFeatures(layer, field):
    ''' set up labeling for layer '''
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
    #UPDATE
    #if isPro: #Update for automated test
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

def ColIdxToXlName(index):
    ''' Converts an index into a letter, labeled like excel columns, A to Z, AA to ZZ, etc.'''
    ordA = ord('A')
    ordZ = ord('Z')
    len = ordZ - ordA + 1          
    s = ""
    while(int(index) >= 0):
        s = chr(int(index) % len + ordA) + s
        index = math.floor(int(index) / len) - 1
    return s
    
def main():
    ''' Main tool method '''
    try:
        #UPDATE
        gisVersion = arcpy.GetInstallInfo()["Version"]
        global appEnvironment
        appEnvironment = Utilities.GetApplication()
        if DEBUG == True: arcpy.AddMessage("App environment: " + appEnvironment)
        global mxd
        global df
        global aprx
        global mapList
        global cellWidth
        global cellHeight
        
        isPro = False
        
        fc = os.path.join("in_memory", "AOI")
        arcpy.CopyFeatures_management(AOI, fc)

        #if gisVersion == "1.0": #Pro: #Update for automated test
        if appEnvironment == "ARCGIS_PRO":
            from arcpy import mp
            aprx = arcpy.mp.ArcGISProject("CURRENT")
            mapList = aprx.listMaps()[0]
            isPro = True
        #else: #Update for automated test
        if appEnvironment == "ARCMAP":
            from arcpy import mapping
            mxd = arcpy.mapping.MapDocument('CURRENT')
            df = arcpy.mapping.ListDataFrames(mxd)[0]
            isPro = False

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
                
                letter = ColIdxToXlName(int(letterIndex))
                secondLetter = ColIdxToXlName(int(secondLetterIndex))    
                
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
                            
        '''
        ' Copy features to output feature class
        '''
        arcpy.CopyFeatures_management(fishnet, outputFeatureClass)
        
        '''
        ' remove the temp feature classes
        '''        
        arcpy.Delete_management(fishnet)
        
        # Get and label the output feature
        #TODO: Update once applying symbology in Pro is fixed.
        #UPDATE
        targetLayerName = os.path.basename(outputFeatureClass)
        if appEnvironment == "ARCGIS_PRO":
            #params = arcpy.GetParameterInfo()
            ## get the symbology from the GRG.lyr
            ##scriptPath = sys.path[0]
            # layerFilePath = os.path.join(scriptPath,r"commondata\userdata\GRG.lyrx")
            #arcpy.AddMessage("Applying Symbology from {0}".format(layerFilePath))
            #params[6].symbology = layerFilePath
            
            arcpy.AddMessage("Do not apply symbology it will be done in the next task step")
            
        elif appEnvironment == "ARCMAP":
                           
            #arcpy.AddMessage("Adding features to map (" + str(targetLayerName) + ")...")
            
            #arcpy.MakeFeatureLayer_management(outputFeatureClass, targetLayerName)
            
            # create a layer object
            #layer = arcpy.mapping.Layer(targetLayerName)            
            
            # get the symbology from the NumberedStructures.lyr
            #layerFilePath = os.path.join(os.getcwd(),"data\Layers\GRG.lyr")
            #layerFilePath = os.path.join(os.path.dirname(os.path.dirname(__file__)),"layers\GRG.lyr")
            
            # apply the symbology to the layer
            #arcpy.ApplySymbologyFromLayer_management(layer, layerFilePath)
            
            # add layer to map
            #arcpy.mapping.AddLayer(df, layer, "AUTO_ARRANGE")
            
            # find the target layer in the map
            #mapLyr = arcpy.mapping.ListLayers(mxd, targetLayerName)[0]  

            #arcpy.AddMessage("Labeling output features (" + str(targetLayerName) + ")...")
            # Work around needed as ApplySymbologyFromLayer_management does not honour labels
            #labelLyr = arcpy.mapping.Layer(layerFilePath)
            # copy the label info from the source to the map layer
            #mapLyr.labelClasses = labelLyr.labelClasses
            # turn labels on
            #mapLyr.showLabels = True
            arcpy.AddMessage("Non-map environment, skipping labeling based on best practices")
        else:
            arcpy.AddMessage("Non-map environment, skipping labeling...")

        # Set tool output
        arcpy.SetParameter(6, outputFeatureClass)

        ### Apply symbology to the GRG layer
        ###UPDATE
        ###symbologyPath = os.path.dirname(workspace) + "\\Layers\GRG.lyr"
        ###arcpy.ApplySymbologyFromLayer_management(layer, symbologyPath)

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

# MAIN =============================================
if __name__ == "__main__":
    main()


