#----------------------------------------------------------------------------------
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
#----------------------------------------------------------------------------------
# GeometryConverter.py
# Description: Convert Points between formats used by Desktop and Runtime Military Message
#----------------------------------------------------------------------------------

import SymbolDictionary
import DictionaryConstants
import os
import math
import arcpy

def getStringFromXY(x, y) : 
    return str(x) + "," + str(y)

def getXYFromString(pointString) : 
    if "," in pointString : 
        x = float(pointString.split(',')[0])
        y = float(pointString.split(',')[1])
    else :
        x = 0 
        y = 0
    return x, y

def getXYFromListAtIndex(pointList, index) :
    if index >= len(pointList) :
        return 0, 0
    else :
        point = pointList[index]
        return getXYFromString(point)

def getmaxmin(pointList) :

    minx = float('nan')
    miny = float('nan')
    maxx = float('nan')
    maxy = float('nan')

    if not (pointList is None ) : 
        first = True
        for point in pointList: 
            x, y = getXYFromString(point)
            if first :
                minx = x
                miny = y 
                maxx = x
                maxy = y
                first = False
            else :
                if x > maxx :
                    maxx = x
                elif x < minx :
                    minx = x
                elif y > maxy :
                    maxy = y
                elif y < miny :
                    miny = y

    return minx, miny, maxx, maxy

def getEnvelopeLengthWidthCenterXY(pointList) :
    minx, miny, maxx, maxy = getmaxmin(pointList) 

    if math.isnan(minx) or math.isnan(miny) or math.isnan(maxx) or math.isnan(maxy) :
        return 0.0, 0.0, 0.0, 0.0

    length = math.fabs(maxy - miny)
    width =  math.fabs(maxx - minx)

    centerX = minx + (width / 2.0)
    centerY = miny + (length / 2.0)

    return length, width, centerX, centerY

def getEnvelopeFromCenterXYLengthWidth(x, y, length, width) :

    halfWidth  = width / 2.0
    halfLength = length / 2.0

    bounding = []
    bounding.append(getStringFromXY(x - halfWidth, y + halfLength)) # upper left
    bounding.append(getStringFromXY(x - halfWidth, y - halfLength)) # lower left 
    bounding.append(getStringFromXY(x + halfWidth, y - halfLength)) # lower right
    bounding.append(getStringFromXY(x + halfWidth, y + halfLength)) # upper right

    return bounding

def minimumBoundingEnvelope(pointList) :

    minx, miny, maxx, maxy = getmaxmin(pointList) 

    if math.isnan(minx) or math.isnan(miny) or math.isnan(maxx) or math.isnan(maxy) :
        return None

    bounding = []
    bounding.append(getStringFromXY(minx, maxy)) # upper left
    bounding.append(getStringFromXY(minx, miny)) # lower left 
    bounding.append(getStringFromXY(maxx, miny)) # lower right
    bounding.append(getStringFromXY(maxx, maxy)) # upper right

    return bounding
        
def getLength(x0, y0, x1, y1) : 
    return math.sqrt((x1-x0)**2 + (y1-y0)**2)        
    
def degreesToRadians(degrees) : 
    return (degrees * math.pi) / 180.0

def radiansToDegrees(radians) : 
    return (radians * (180.0 / math.pi))

# Angle between 2 points measured from X Axis
def getAngle(x1, y1, x2, y2) :
    try : 
        degrees = radiansToDegrees(math.atan2(y2 - y1, x2 - x1))
    except : 
        # should only happen if length == 0 
        degrees = 0.0
    return degrees 

def getAngleFromY(x1, y1, x2, y2) :
    try : 
        degrees = radiansToDegrees(math.atan2(x2 - x1, y2 - y1))
    except : 
        # should only happen if length == 0 
        degrees = 0.0
    return degrees 

def getAzimuth(x1, y1, x2, y2) :
    azimuth = getAngleFromY(x1, y1, x2, y2)
    # azimuth = radiansToDegrees(math.atan2(x2 - x1, y2 - y1)) # getAngle(x1, y1, x2, y2)
    if (azimuth < 0.0) : 
      azimuth += 360.0

    return azimuth

# just returns slope as either 1 or -1 (for determining slope of line)
def getIncline(x1, y1, x2, y2) :
    angleFromY = getAngleFromY(x1, y1, x2, y2)
    # angle = radiansToDegrees(math.atan2(x2 - x1, y2 - y1)) # getAngle(x1, y1, x2, y2)

    if (angleFromY >= 0.0) : # and (angle < 180.0): # and (angle < 90.0)) or ((angle > 180.0) and (angle < 270.0)):
        return -1.0
    else :
        return 1.0        

def scale(scaleFactor, x0, y0, x1, y1) : # Vector V0(x0,y0)->V1(x1,y1)

    dx = x1 - x0
    dy = y1 - y0

    sx = scaleFactor * dx
    sy = scaleFactor * dy

    x = sx + x0
    y = sy + y0

    return x, y

def rotate(angle, x0, y0, x1, y1) : # rotate (x1, y1) about (x0, y0) by angle (degrees)

    theta = degreesToRadians(angle)

    cosa = math.cos(theta)
    sina = math.sin(theta)
       
    xp = x0 + ((x1 - x0) * cosa) - ((y1 - y0) * sina)
    yp = y0 + ((y1 - y0) * cosa) + ((x1 - x0) * sina)
    
    return xp, yp

def rotateAndScale(angle, scaleFactor, x0, y0, x1, y1) : 
    rx, ry = rotate(angle, x0, y0, x1, y1)
    x, y = scale(scaleFactor, x0, y0, rx, ry) # Vector V0(x1,y1)->V1(rx,ry)
    return x, y

def getMetersFromLength(distance, wkid) :
    ##TODO: if needed plug in call to convert distance to meters
    ## determine if SR is in meters, if not project to meters
    print "getMetersFromLength"
    return distance

def getMapUnitsFromMeters(meters, wkid) :
    ##TODO: if needed plug in call to convert meters to map units
    ## determine if SR is in meters, if not project to meters to dataset SR
    print "getMapUnitsFromMeters"
    return meters

class GeometryConverter() :
    """description of class"""

    def __init__(self, symbolDictionaryIn) :
        print "GeometryConverter Init"
        if (symbolDictionaryIn is None) : 
            print "SymbolDictionary is None"
        self.symbolDictionary = symbolDictionaryIn
        self.ignoreSecondTwoLine = False

    def getSymbolDictionary(self) :
        return self.symbolDictionary

    def expectedGeometryType(self, sic) :
        if (sic == None) :
            return DictionaryConstants.UNKNOWN_GEOMETRY_STRING
        return self.symbolDictionary.symbolIdToGeometryType(sic)

    def requiresConversion(self, sic) :

        if (sic == None) :
            return False

        geoType = self.symbolDictionary.symbolIdToGeometryType(sic)
        geoConversion = self.symbolDictionary.symbolIdToGeometryConversionType(sic)

        if (geoType == DictionaryConstants.POINT_STRING) :
            return False
        elif (geoType == DictionaryConstants.LINE_STRING) \
            & (geoConversion == DictionaryConstants.GCT_POLYLINE) :
            return False
        elif (geoType == DictionaryConstants.AREA_STRING) \
            & (geoConversion == DictionaryConstants.GCT_POLYGON) :
            return False
        else :
            return True

    def geometrytoControlPoints(self, sic, control_points, attributes) : 

        if (sic == None) or (control_points == None) :
            return None, DictionaryConstants.CONVERSION_ERROR_VALIDATION

        inPoints = control_points.split(';')
        outPoints = None
        pointCount = len(inPoints)

        geoType = self.symbolDictionary.symbolIdToGeometryType(sic)
        geoConversion = self.symbolDictionary.symbolIdToGeometryConversionType(sic)

        wkid = 4326 # default to WGS84
        if attributes.has_key(DictionaryConstants.Tag_Wkid) : 
            wkid = int(attributes[DictionaryConstants.Tag_Wkid])

        conversionNotes = None

        if geoConversion == DictionaryConstants.GCT_POINT : 
            print "GCT_POINT"
            if (pointCount != 1) or (geoType != DictionaryConstants.POINT_STRING) :
                conversionNotes = geoConversion + " - Conversion Failed, not Point"
                return None, conversionNotes
            else :
                outPoints = inPoints

        elif geoConversion == DictionaryConstants.GCT_POLYLINE : 
            print "GCT_POLYLINE"
            if (pointCount < 2) or (geoType != DictionaryConstants.LINE_STRING) :
                conversionNotes = geoConversion + " - Conversion Failed, not Line"
                return None, conversionNotes
            else :
                outPoints = inPoints

        elif geoConversion == DictionaryConstants.GCT_POLYGON  :             	
            print "GCT_POLYGON"
            if (pointCount < 3) or (geoType != DictionaryConstants.AREA_STRING) :
                conversionNotes = geoConversion + " - Conversion Failed, not Polygon"
                return None, conversionNotes
            else :
                outPoints = inPoints

        elif geoConversion == DictionaryConstants.GCT_INDETERMINATE  :  
            conversionNotes = geoConversion + " - Unexpected Conversion type"             	 	
            return None, conversionNotes 

        elif geoConversion == DictionaryConstants.GCT_ARROW  :               	
            print "GCT_ARROW"
            print "Reverse the points"

            if pointCount < 2 :
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            outPoints = inPoints
            outPoints.reverse()

        elif geoConversion == DictionaryConstants.GCT_ARROWWITHOFFSET :  	    
            print "GCT_ARROWWITHOFFSET"
            print "Reverse the points and add offset Point"

            if pointCount < 2 :
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            outPoints = inPoints
            outPoints.reverse()

            # calculate arrowhead point
            x0, y0 = getXYFromListAtIndex(outPoints, 1)
            x1, y1 = getXYFromListAtIndex(outPoints, 0)

            rsx, rsy = rotateAndScale(45, 0.5, x0, y0, x1, y1) 
            lastPoint = getStringFromXY(rsx, rsy)

            outPoints.append(lastPoint)

        elif geoConversion == DictionaryConstants.GCT_ARROWWITHTAIL :     	 	
            print "GCT_ARROWWITHTAIL"
            print "Use 1st and last point, and calculate the tail points 2, 3"

            if pointCount < 2 :
                print ">= 2 points required"
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            startPoint = inPoints[0]
            endPoint = inPoints[pointCount-1] # pointCount - just in case more than 2 points were input in ArcMap

            x0, y0 = getXYFromString(startPoint)
            x1, y1 = getXYFromString(endPoint)

            magnitude = getLength(x0, y0, x1, y1)

            # make tail points by just rotating the original line 
            x2, y2 = rotate(90.0, x0, y0, x1, y1)
            x3, y3 = rotate(-90.0, x0, y0, x1, y1)

            outPoints = [] 
            outPoints.append(getStringFromXY(x1, y1))
            outPoints.append(getStringFromXY(x2, y2))
            outPoints.append(getStringFromXY(x3, y3))

        elif geoConversion == DictionaryConstants.GCT_CIRCLE or \
            geoConversion == DictionaryConstants.GCT_CIRCULAR : 			
            print "GCT_CIRCLE / GCT_CIRCULAR"
            print "Get Bounding Rectangle and create center and circle point"
            if pointCount == 1 :
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT
            if pointCount == 2 :
                centerPoint = inPoints[0]
                circlePoint = inPoints[1]
            elif pointCount > 3 :
                minx, miny, maxx, maxy = getmaxmin(inPoints) 

                if math.isnan(minx) or math.isnan(miny) or math.isnan(maxx) or math.isnan(maxy):
                    # get envelope failed
                    print "Could not determine circle envelope"
                else :
                    midx = (minx + maxx) / 2.0
                    midy = (miny + maxy) / 2.0

                    centerPoint = getStringFromXY(midx, midy)
                    circlePoint = getStringFromXY(midx, miny) 
                
            xc, yc = getXYFromString(centerPoint)
            xr, yr = getXYFromString(circlePoint)

            radius = getLength(xc, yc,  xr, yr)            

            if radius > 0.0 :
                attributes[DictionaryConstants.Tag_Radius] = getMetersFromLength(radius, wkid)
                outPoints = [] 
                outPoints.append(centerPoint)
                # GCT_CIRCLE has center & cirlce point
                if geoConversion == DictionaryConstants.GCT_CIRCLE : 
                    outPoints.append(circlePoint) 
            else :  
                # if radius == 0 it was probably a source circle geometry (start point = end point)
                msg = "IMPORTANT: Circle geometries are not supported by ArcPy"
                print msg
                arcpy.AddWarning(msg)
                msg = "You will need to use a polyline, polygon or run GP.Densify_edit Tool"
                print msg
                arcpy.AddWarning(msg)

        elif geoConversion == DictionaryConstants.GCT_FREEHANDARROW	:		
            print "GCT_FREEHANDARROW"
            print "Use 1st and last point, and calculate the 3rd, middle point half way between them."

            if pointCount < 2 :
                print ">= 2 points required"
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            if pointCount == 2 : 
                startPoint = inPoints[0]
                endPoint = inPoints[-1]   
    
                xs, ys = getXYFromString(startPoint)
                xe, ye = getXYFromString(endPoint)
    
                # make tail points by just rotating/scaling the original line 
                incline = getIncline(xs, ys, xe, ye)
                x3, y3 = rotateAndScale(incline * 30.0, 0.5, xs, ys, xe, ye)
                middlePoint = getStringFromXY(x3, y3) 

            else : # pointCount > 2 
                
                startPoint = inPoints[0] # pointCount - just in case more than 2 points were input in ArcMap
                endPoint = inPoints[-1] 
                
                middlePointIndex = int((pointCount - 1) / 2)   
                if (middlePointIndex > 0) and (middlePointIndex < (pointCount - 1)) :             
                    middlePoint = inPoints[middlePointIndex]
                else :
                    middlePoint = inPoints[1]     
                    
            outPoints = [] 
            outPoints.append(startPoint)
            outPoints.append(endPoint)
            outPoints.append(middlePoint)

        elif geoConversion == DictionaryConstants.GCT_FREEHANDLINE :         	
            print "GCT_FREEHANDLINE"
            print "Use 1st and last point, and calculate the 3rd, middle point half way between them."

            if pointCount < 2 :
                print ">= 2 points required"
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            startPoint = inPoints[0]
            endPoint = inPoints[pointCount-1] # pointCount - just in case more than 2 points were input in ArcMap

            xs, ys = getXYFromString(startPoint)
            xe, ye = getXYFromString(endPoint)

            # make tail points by just rotating/scaling the original line 
            # x3, y3 = rotateAndScale(45.0, 0.7, xs, ys, xe, ye)
            
            # Workaround: Just use middle point to handle cases when > 3 points
            middlePointIndex = int((pointCount - 1) / 2)
            middlePoint = inPoints[middlePointIndex]                        

            outPoints = [] 
            outPoints.append(startPoint)
            outPoints.append(endPoint)
            # outPoints.append(getStringFromXY(x3, y3))
            outPoints.append(middlePoint)

        elif geoConversion == DictionaryConstants.GCT_FREEHANDREVERSEARROW 	:
            print "GCT_FREEHANDREVERSEARROW"
            print "Use 1st and last point, and calculate the 3rd, middle point half way between them."

            if pointCount < 2 :
                print ">= 2 points required"
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            if pointCount == 2 : 
                startPoint = inPoints[0]
                endPoint = inPoints[pointCount-1] # pointCount - just in case more than 2 points were input in ArcMap
    
                xs, ys = getXYFromString(startPoint)
                xe, ye = getXYFromString(endPoint)
    
                # make tail points by just rotating/scaling the original line 
                incline = getIncline(xs, ys, xe, ye)
                x3, y3 = rotateAndScale((incline * 30.0), 0.5, xs, ys, xe, ye)
                
                middlePoint = getStringFromXY(x3, y3)
            else : # pointCount > 2 
                
                startPoint = inPoints[-1] # pointCount - just in case more than 2 points were input in ArcMap
                endPoint = inPoints[0] 
                
                middlePointIndex = int((pointCount - 1) / 2)   
                if (middlePointIndex > 0) and (middlePointIndex < (pointCount - 1)) :             
                    middlePoint = inPoints[middlePointIndex]
                else :
                    middlePoint = inPoints[1]                

            outPoints = [] 
            outPoints.append(startPoint)
            outPoints.append(endPoint)
            outPoints.append(middlePoint)

        elif geoConversion == DictionaryConstants.GCT_FREEHANDU  :         	
            print "GCT_FREEHANDU"

            if pointCount < 2 :
                print ">= 2 points required"
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            print "Take input points 1, 2 then derive envelope with points 1, 2, 4, 3"

            if pointCount == 4 : 
                # if it is 4 points, just use the original points
                outPoints = inPoints
                outPoints.reverse()
            else :
                startPoint = inPoints[0]
                endPoint = inPoints[-1] # pointCount - just in case more than 2 points were input in ArcMap

                xs, ys = getXYFromString(startPoint)
                xe, ye = getXYFromString(endPoint)

                incline = getIncline(xs, ys, xe, ye)
                print "Incline = " + str(incline)

                incline = 1.0 # getIncline(xs, ys, xe, ye)

                # make tail points by just rotating/scaling the original line 
                x2, y2 = rotateAndScale(incline*60.0, 1.2, xs, ys, xe, ye)
                x3, y3 = rotateAndScale(incline*90.0, 1.0, xs, ys, xe, ye)

                outPoints = [] 
                outPoints.append(endPoint)
                outPoints.append(getStringFromXY(x2, y2))
                outPoints.append(getStringFromXY(x3, y3))
                outPoints.append(startPoint)

            if pointCount >= 4 :
                print "> 4 points use bounding envelope with points 1, 2, 3, 4"
                bounding = minimumBoundingEnvelope(inPoints)
                if bounding != None :
                    # TODO need to determine polygon winding (clockwise or counter) of original points
                    # to determing if arrows are pointed left or right
                    outPoints = [] 
                    outPoints.append(bounding[0]) # upper left
                    outPoints.append(bounding[3]) # upper right
                    outPoints.append(bounding[2]) # lower right
                    outPoints.append(bounding[1]) # lower left                                                                

        elif geoConversion == DictionaryConstants.GCT_HOOK :                 	
            print "GCT_HOOK"
            
            print "Points ordered 1, 2, ... n -> n, 3/4n, 0"
            
            # OLD: Turns out points are not really ordered this way in ArcMap
            # print "Points ordered 1, 2 -> 2, 1, derived 3(90 degrees to line 21)"

            if pointCount < 2 :
                print ">= 2 points required"
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT
            
            if pointCount == 2 :
                
                print "Points ordered 1, 2 -> 2, 1, derived 3(90 degrees to line 21)"

                startPoint = inPoints[-1] # pointCount - just in case more than 2 points were input in ArcMap
                endPoint = inPoints[0] 
    
                xs, ys = getXYFromString(startPoint)
                xe, ye = getXYFromString(endPoint)
    
                # make tail points by just rotating/scaling the original line 
                x3, y3 = rotateAndScale(30.0, 1.2, xs, ys, xe, ye)  # 1.2 = 2 / sqrt(3) 
    
                middlePoint = getStringFromXY(x3, y3)
            else : # pointCount > 2 
                
                startPoint = inPoints[-1] # pointCount - just in case more than 2 points were input in ArcMap
                endPoint = inPoints[0] 
                
                middlePointIndex = int((pointCount - 1) * 0.75)   
                if (middlePointIndex > 0) and (middlePointIndex < (pointCount - 1)) :             
                    middlePoint = inPoints[middlePointIndex]
                else :
                    middlePoint = inPoints[1]
                
            outPoints = [] 
            outPoints.append(startPoint)
            outPoints.append(middlePoint)                
            outPoints.append(endPoint)

        elif geoConversion == DictionaryConstants.GCT_HORNS	:				
            print "GCT_HORNS"
            print "Take input points 1, 2 then derive envelope with points 1, 2, 4, 3"

            if pointCount < 2 :
                print ">= 2 points required"
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            startPoint = inPoints[0]
            endPoint = inPoints[-1] # pointCount - just in case more than 2 points were input in ArcMap

            xs, ys = getXYFromString(startPoint)
            xe, ye = getXYFromString(endPoint)

            # make tail points by just rotating/scaling the original line 
            x1, y1 = rotateAndScale(90.0, 1.5, xs, ys, xe, ye)
            x2, y2 = rotateAndScale(-90.0, 1.5, xs, ys, xe, ye)
            x3, y3 = rotateAndScale(45.0, 1.5, xs, ys, xe, ye)
            x4, y4 = rotateAndScale(-45.0, 1.5, xs, ys, xe, ye)

            outPoints = [] 
            outPoints.append(getStringFromXY(x1, y1))
            outPoints.append(getStringFromXY(x2, y2))
            outPoints.append(getStringFromXY(x3, y3))
            outPoints.append(getStringFromXY(x4, y4))

        elif geoConversion == DictionaryConstants.GCT_OPENTRIANGLE	:		
            print "GCT_OPENTRIANGLE"
            print "Points ordered 1, 2, 3 -> 2, 1, 3, if more than 3 points, only 1st 3 points are used"

            if pointCount < 3 :
                print "3 Points Required"
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT
            elif pointCount > 3 :
                print "WARNING: more than 3 points in input Geometry, dropping extra points"

            outPoints = [] 
            outPoints.append(inPoints[1])
            outPoints.append(inPoints[0])
            outPoints.append(inPoints[2])

        elif (geoConversion == DictionaryConstants.GCT_PARALLELLINES) or \
            (geoConversion == DictionaryConstants.GCT_PARALLELLINESMIDLINE)  :	
            print "GCT_PARALLELLINESMIDLINE"
            print "Points ordered 1, 2 -> 1, 2, derived 3(at mid point of 1, 2)"

            if pointCount < 2 :
                print ">= 2 points required"
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            startPoint = inPoints[0]
            endPoint = inPoints[-1] # pointCount - just in case more than 2 points were input in ArcMap

            xs, ys = getXYFromString(startPoint)
            xe, ye = getXYFromString(endPoint)

            # Workaround: Just use middle point to handle cases when > 3 points
            # middlePointIndex = int((pointCount - 1) / 2)
            # middlePoint = inPoints[middlePointIndex]    
            
            # make tail points by just rotating/scaling the original line 
            x3, y3 = rotateAndScale(30.0, 0.6, xs, ys, xe, ye) # 0.5 * 1.2 = 2 / sqrt(3) 

            outPoints = [] 
            outPoints.append(startPoint)
            outPoints.append(endPoint)
            # outPoints.append(middlePoint) # getStringFromXY(x3, y3))
            outPoints.append(getStringFromXY(x3, y3))

        elif geoConversion == DictionaryConstants.GCT_PARALLELLINESWITHTICKS :
            print "GCT_PARALLELLINESWITHTICKS"
            print "Take input points 1, 2 then derive envelope with points 1, 2, 4, 3"

            if pointCount < 2 :
                print ">= 2 points required"
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            startPoint = inPoints[0]
            endPoint = inPoints[-1] # pointCount - just in case more than 2 points were input in ArcMap

            xs, ys = getXYFromString(startPoint)
            xe, ye = getXYFromString(endPoint)

            # make tail points by just rotating/scaling the original line 
            
            incline = getIncline(xs, ys, xe, ye)
                        
            x1, y1 = rotateAndScale(-90.0 * incline, 0.6, xs, ys, xe, ye)
            x2, y2 = rotateAndScale(-30.0 * incline, 1.2, xs, ys, xe, ye)
            x3, y3 = rotateAndScale(90.0 * incline, 0.6, xs, ys, xe, ye)
            x4, y4 = rotateAndScale(30.0 * incline, 1.2, xs, ys, xe, ye)

            outPoints = [] 
            outPoints.append(getStringFromXY(x1, y1))
            outPoints.append(getStringFromXY(x2, y2))
            outPoints.append(getStringFromXY(x3, y3))
            outPoints.append(getStringFromXY(x4, y4))

        elif (geoConversion == DictionaryConstants.GCT_RECTANGULAR) or \
            (geoConversion == DictionaryConstants.GCT_RECTANGULAR1PT) :        	
            print "GCT_RECTANGULAR/GCT_RECTANGULAR1PT"

            length = 0.0
            width = 0.0
            orientation = 0.0

            if pointCount >= 3 : 
                length, width, centerX, centerY = getEnvelopeLengthWidthCenterXY(inPoints)

                if (length > 0.0) and (width > 0.0) :
                    attributes[DictionaryConstants.Tag_Length] = getMetersFromLength(length, wkid)
                    attributes[DictionaryConstants.Tag_Width] = getMetersFromLength(width, wkid)

                    outPoints = [] 
                    if geoConversion == DictionaryConstants.GCT_RECTANGULAR : 
                        outPoints.append(getStringFromXY(centerX - (length / 2.0), centerY))
                        outPoints.append(getStringFromXY(centerX + (length / 2.0), centerY))
                    if geoConversion == DictionaryConstants.GCT_RECTANGULAR1PT : 
                        outPoints.append(getStringFromXY(centerX, centerY))
                        if orientation > 0.0 :
                            attributes[DictionaryConstants.Tag_Orientation] = orientation
                                                    
        elif geoConversion == DictionaryConstants.GCT_T :                    	
            print "GCT_T"
            print "Points ordered 1, 2 -> 1, 2, derived 3(3/4 length of Line 12)"

            if pointCount < 2 :
                print ">= 2 points required"
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            startPoint = inPoints[0]
            endPoint = inPoints[-1] # pointCount - just in case more than 2 points were input in ArcMap

            xs, ys = getXYFromString(startPoint)
            xe, ye = getXYFromString(endPoint)

            # make tail points by just rotating/scaling the original line 
            x3, y3 = rotateAndScale(30.0, 0.8, xe, ye, xs, ys) 

            outPoints = [] 
            outPoints.append(startPoint)
            outPoints.append(endPoint)
            outPoints.append(getStringFromXY(x3, y3))

        elif geoConversion == DictionaryConstants.GCT_TRIPLEARROW :       	    
            print "GCT_TRIPLEARROW"
            print "Points ordered 1, 2 -> derived 1, derived 2, derived 3"

            if pointCount < 2 :
                print ">= 2 points required"
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            startPoint = inPoints[0] 
            endPoint = inPoints[-1]  # last point - just in case more than 2 points were input in ArcMap

            xs, ys = getXYFromString(startPoint)
            xe, ye = getXYFromString(endPoint)

            # make tail points by just rotating/scaling the original line 
            x1, y1 = rotateAndScale(90.0, 0.6, xs, ys, xe, ye)
            x2, y2 = rotateAndScale(-90.0, 0.6, xs, ys, xe, ye)
            x3, y3 = rotateAndScale(-30.0, 1.2, xs, ys, xe, ye) # 1.2 = 2 / sqrt(3) 

            outPoints = [] 
            outPoints.append(getStringFromXY(x1, y1))
            outPoints.append(getStringFromXY(x2, y2))
            outPoints.append(getStringFromXY(x3, y3))

        elif (geoConversion == DictionaryConstants.GCT_TWOLINE) or \
             (geoConversion == DictionaryConstants.GCT_TWOLINE3OR4PT) :      
            
            if self.ignoreSecondTwoLine :
                # IMPORTANT: assumes the 2nd part will always be next
                self.ignoreSecondTwoLine = False
                return None, DictionaryConstants.CONVERSION_IGNORE_SECOND_LINE
                	
            print "GCT_TWOLINE (2PT) or (3OR4PT)"
            print "Points ordered 1, 2 -> 1, 2, derived 3 (45 degrees rotated)"

            if pointCount < 2 :
                print ">= 2 points required"
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            startPoint = inPoints[0] 
            endPoint = inPoints[1] 

            xs, ys = getXYFromString(startPoint)
            xe, ye = getXYFromString(endPoint)

            x3, y3 = rotate(45.0, xs, ys, xe, ye)

            outPoints = [] 
            outPoints.append(startPoint)
            outPoints.append(endPoint)
            outPoints.append(getStringFromXY(x3, y3))

            self.ignoreSecondTwoLine = True

        elif geoConversion == DictionaryConstants.GCT_UORTSHAPE  :         	
            print "GCT_UORTSHAPE"
            print "Points ordered 1, 2 -> derived 1, derived 2, 3(originally pt 1)"

            if pointCount < 2 :
                print ">= 2 points required"
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            startPoint = inPoints[0]
            endPoint = inPoints[-1] # pointCount - just in case more than 2 points were input in ArcMap

            xs, ys = getXYFromString(startPoint)
            xe, ye = getXYFromString(endPoint)

            # make tail points by just rotating/scaling the original line 
            x1, y1 = rotateAndScale(-30.0, 1.2, xs, ys, xe, ye) # 1.2 = 2 / sqrt(3) 
            x2, y2 = rotateAndScale(30.0, 1.2, xs, ys, xe, ye)

            outPoints = [] 
            outPoints.append(getStringFromXY(x1, y1))
            outPoints.append(getStringFromXY(x2, y2))
            outPoints.append(startPoint)
        
        if not ((geoConversion == DictionaryConstants.GCT_TWOLINE) or \
             (geoConversion == DictionaryConstants.GCT_TWOLINE3OR4PT)) :      
            self.ignoreSecondTwoLine = False

        # Conversion done, now format output and return message
        msg = "Geometry Conversion: " + geoConversion
        if outPoints is None :
            msg =  "Geometry Conversion: " + geoConversion + " failed. Returning original points."
            print msg
            arcpy.AddWarning(msg)
            outPoints = inPoints

        # Convert the point list back to a string before returning
        outPointsString = ""
        for point in outPoints :
            outPointsString += point + ";"

        #remove last ";"        
        if len(outPointsString) > 0 : 
            outPointsString = outPointsString[:-1]

        return outPointsString, msg

    ########################################################################################
    ########################################################################################

    def controlPointsToGeometry(self, sic, control_points, attributes) :        

        inPoints = control_points.split(';')
        outPoints = None

        if not self.requiresConversion(sic) : 
            return inPoints, "No conversion required"

        print "controlPointsToGeometry-->Original Points:"
        for point in inPoints : 
            x = point.split(',')[0]
            y = point.split(',')[1]
            print x, y

        pointCount = len(inPoints)

        geoType = self.symbolDictionary.symbolIdToGeometryType(sic)

        geoConversion = self.symbolDictionary.symbolIdToGeometryConversionType(sic)

        wkid = 4326 # default to WGS84
        if attributes.has_key(DictionaryConstants.Tag_Wkid) : 
            wkid = int(attributes[DictionaryConstants.Tag_Wkid])

        if geoConversion == DictionaryConstants.GCT_POINT : 
            print "GCT_POINT"
            if (pointCount != 1) or (geoType != DictionaryConstants.POINT_STRING) :
                conversionNotes = geoConversion + " - Conversion Failed, not Point"
                return None, conversionNotes
            else :
                outPoints = inPoints

        elif geoConversion == DictionaryConstants.GCT_POLYLINE : 
            print "GCT_POLYLINE"
            if (pointCount < 2) or (geoType != DictionaryConstants.LINE_STRING) :
                conversionNotes = geoConversion + " - Conversion Failed, not Line"
                return None, conversionNotes
            else :
                outPoints = inPoints

        elif geoConversion == DictionaryConstants.GCT_POLYGON  :             	
            print "GCT_POLYGON"
            if (pointCount < 3) or (geoType != DictionaryConstants.AREA_STRING) :
                conversionNotes = geoConversion + " - Conversion Failed, not Polygon"
                return None, conversionNotes
            else :
                outPoints = inPoints

        elif geoConversion == DictionaryConstants.GCT_INDETERMINATE  :   	 	
            conversionNotes = geoConversion + " - Unexpected Conversion type"             	 	
            return None, conversionNotes 

        elif geoConversion == DictionaryConstants.GCT_ARROW  :               	
            print "GCT_ARROW"
            print "Reverse the points"
            outPoints = inPoints
            outPoints.reverse()

        elif geoConversion == DictionaryConstants.GCT_ARROWWITHOFFSET :  	    
            print "GCT_ARROWWITHOFFSET"
            print "Discard last point, and reverse the remaining points (>3 points required)"

            if pointCount < 2 :
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            outPoints = inPoints[0:-1]
            outPoints.reverse()

        elif geoConversion == DictionaryConstants.GCT_ARROWWITHTAIL :     	 	
            print "GCT_ARROWWITHTAIL"
            print "Use 1st point, and calculate the midpoint of 2, 3 (>3 points required)"

            if pointCount < 3 :
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            x0, y0 = getXYFromString(inPoints[2])
            x1, y1 = getXYFromString(inPoints[1]) 

            midPointX, midPointY = scale(0.5, x0, y0, x1, y1) 

            outPoints = []
            outPoints.append(getStringFromXY(midPointX, midPointY))
            outPoints.append(inPoints[0])

        elif geoConversion == DictionaryConstants.GCT_CIRCLE :					
            print "GCT_CIRCLE"
            print "1, 2, -> circle with center pt 1, arcpoint start point 2, 330 degrees of arc"

            if pointCount != 2 :
                print "2 points required"
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            x1, y1 = getXYFromString(inPoints[0])
            x2, y2 = getXYFromString(inPoints[1]) 
            
            radius = getLength(x1, y1,  x2, y2)

            if radius <= 0.0 :
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_RADIUS

            startAzimuth = getAzimuth(x1, y1,  x2, y2)

            endAzimuth = startAzimuth + 330.0

            outPoints = []
            azi = startAzimuth
            while azi < endAzimuth : 
                x = x1 + radius * math.sin(degreesToRadians(azi))
                y = y1 + radius * math.cos(degreesToRadians(azi))
                azi += 10.0 
                outPoints.append(getStringFromXY(x, y))

        elif geoConversion == DictionaryConstants.GCT_CIRCULAR :           	
            print "GCT_CIRCULAR"

            radius = 0.0
            if attributes.has_key(DictionaryConstants.Tag_Radius) :
                radius = float(attributes[DictionaryConstants.Tag_Radius])

            radius = getMapUnitsFromMeters(radius, wkid)

            outPoints = []

            if (pointCount == 1 ) :
                if radius <= 0.0 :
                    return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_RADIUS

                x1, y1 = getXYFromString(inPoints[0])
                azi = 0.0
                while azi < 360.0 : 
                    x = x1 + radius * math.sin(degreesToRadians(azi))
                    y = y1 + radius * math.cos(degreesToRadians(azi))
                    azi += 10.0 
                    outPoints.append(getStringFromXY(x, y))
            elif (pointCount > 2) : 
                outPoints = inPoints

        elif geoConversion == DictionaryConstants.GCT_FREEHANDARROW	:		
            print "GCT_FREEHANDARROW"
            print "1, 2, 3 -> 1, 2"

            if pointCount != 3 :
                print "3 points required"
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            outPoints = []
            outPoints.append(inPoints[0])
            # TODO: may need to add interpolation points along an arc between these 2 points 
            outPoints.append(inPoints[1])

        elif geoConversion == DictionaryConstants.GCT_FREEHANDLINE :         	
            print "GCT_FREEHANDLINE"
            print "1, 2, 3 -> 1, 3, 2"

            if pointCount != 3 :
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            outPoints = []
            outPoints.append(inPoints[0])
            outPoints.append(inPoints[2])
            outPoints.append(inPoints[1])

        elif geoConversion == DictionaryConstants.GCT_FREEHANDREVERSEARROW 	:
            print "GCT_FREEHANDREVERSEARROW"
            print "1, 2, 3 -> 2, 3, 1"

            if pointCount != 3 :
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            outPoints = []
            outPoints.append(inPoints[1])
            outPoints.append(inPoints[2])
            outPoints.append(inPoints[0])

        elif geoConversion == DictionaryConstants.GCT_FREEHANDU  :         	
            print "GCT_FREEHANDU"
            print "Reverse Points"
            outPoints = inPoints
            # TODO: add interpolation circular arc between pts 2,3 (center is midpoint of L23)
            outPoints.reverse()

        elif geoConversion == DictionaryConstants.GCT_HOOK :                 	
            print "GCT_HOOK"
            print "Points ordered 1, 2, 3 -> 2, 1"

            if pointCount != 3 :
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            outPoints = []
            outPoints.append(inPoints[1])
            outPoints.append(inPoints[0])

        elif geoConversion == DictionaryConstants.GCT_HORNS	:				
            print "GCT_HORNS"
            print "Take input points 1, 2, 3, 4 then derive 1 (midpt of 1,2), 2 (midpt of 3, 4)"

            if pointCount < 4 :
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            x1, y1 = getXYFromString(inPoints[0])
            x2, y2 = getXYFromString(inPoints[1]) 
            x3, y3 = getXYFromString(inPoints[2])
            x4, y4 = getXYFromString(inPoints[3]) 

            midPointX1, midPointY1 = scale(0.5, x1, y1, x2, y2) 
            midPointX2, midPointY2 = scale(0.5, x3, y3, x4, y4) 

            outPoints = []
            outPoints.append(getStringFromXY(midPointX1, midPointY1))
            outPoints.append(getStringFromXY(midPointX2, midPointY2))

        elif geoConversion == DictionaryConstants.GCT_OPENTRIANGLE	:		
            print "GCT_OPENTRIANGLE"
            print "Points ordered 2, 1, 3 -> 1, 2, 3"

            if pointCount != 3 :
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            outPoints = [] 
            outPoints.append(inPoints[1])
            outPoints.append(inPoints[0])
            outPoints.append(inPoints[2])

        elif (geoConversion == DictionaryConstants.GCT_PARALLELLINES) or \
            (geoConversion == DictionaryConstants.GCT_PARALLELLINESMIDLINE) or \
            (geoConversion == DictionaryConstants.GCT_T) :	
            print "GCT_PARALLELLINES / GCT_PARALLELLINESMIDLINE"
            print "Points ordered 1, 2, 3  -> 1, 2"

            if not ((pointCount == 2) or (pointCount == 3)) :
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            outPoints = [] 
            outPoints.append(inPoints[0])
            outPoints.append(inPoints[1])

            # TODO: 3rd point should define the width
            # TODO: Refine GCT_PARALLELLINESMIDLINE so it is aligned with the midline, shift it up 

        elif geoConversion == DictionaryConstants.GCT_PARALLELLINESWITHTICKS :
            print "GCT_PARALLELLINESWITHTICKS"
            print "Take input points 1, 2, 3, 4 then derive 1 (midpt of 1,3), 2 (midpt of 2, 4)"

            if pointCount < 4 :
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            x1, y1 = getXYFromString(inPoints[0])
            x2, y2 = getXYFromString(inPoints[1]) 
            x3, y3 = getXYFromString(inPoints[2])
            x4, y4 = getXYFromString(inPoints[3]) 

            midPointX1, midPointY1 = scale(0.5, x1, y1, x3, y3) 
            midPointX2, midPointY2 = scale(0.5, x2, y2, x4, y4) 

            outPoints = []
            outPoints.append(getStringFromXY(midPointX1, midPointY1))
            outPoints.append(getStringFromXY(midPointX2, midPointY2))

        elif (geoConversion == DictionaryConstants.GCT_RECTANGULAR) or \
            (geoConversion == DictionaryConstants.GCT_RECTANGULAR1PT) :        	
            print "GCT_RECTANGULAR/GCT_RECTANGULAR1PT"

            x = 0.0
            y = 0.0
            if pointCount == 1 :
                x, y = getXYFromString(inPoints[0])
            elif pointCount == 2 :
                x0, y0 = getXYFromString(inPoints[0])
                x1, y1 = getXYFromString(inPoints[1])
                x = x0 + ((x1 - x0) / 2.0)
                y = y0 + ((y1 - y0) / 2.0)
            else : 
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT
                
            length = 0.0
            width = 0.0
            orientation = 0.0

            if attributes.has_key(DictionaryConstants.Tag_Length) :
                length = float(attributes[DictionaryConstants.Tag_Length])
                length = getMapUnitsFromMeters(length, wkid)
            if attributes.has_key(DictionaryConstants.Tag_Width) :
                width = float(attributes[DictionaryConstants.Tag_Width])
                width = getMapUnitsFromMeters(width, wkid)
            if attributes.has_key(DictionaryConstants.Tag_Orientation) :
                orientation = float(attributes[DictionaryConstants.Tag_Orientation])

            if (length > 0.0) and (width > 0.0) :
                outPoints = getEnvelopeFromCenterXYLengthWidth(x, y, length, width)
            else :
                return None, "Length/Width not set"
                
        elif geoConversion == DictionaryConstants.GCT_TRIPLEARROW :       	    
            print "GCT_TRIPLEARROW"
            print "1, 2, 3 -> 1, 3" 
            if pointCount != 3 :
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            outPoints = [] 
            outPoints.append(inPoints[0])
            outPoints.append(inPoints[2])
            # TODO move line down

        elif (geoConversion == DictionaryConstants.GCT_TWOLINE) or \
             (geoConversion == DictionaryConstants.GCT_TWOLINE3OR4PT) :      	
                       	
            print "GCT_TWOLINE/GCT_TWOLINE3OR4PT"

            if pointCount < 3 :
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            outPoints = [] 

            if attributes.has_key(DictionaryConstants.Tag_TwoLinesNeeded) and \
                attributes[DictionaryConstants.Tag_TwoLinesNeeded] == "True" :
                print "Second Line"
                outPoints.append(inPoints[0])
                outPoints.append(inPoints[2])
            else :
                print "First Line"
                outPoints.append(inPoints[0])
                outPoints.append(inPoints[1])

        #elif geoConversion == DictionaryConstants.GCT_TWOLINE3OR4PT  :      	
        #    print "GCT_TWOLINE3OR4PT"

        elif geoConversion == DictionaryConstants.GCT_UORTSHAPE  :         	
            print "GCT_UORTSHAPE"
            print "Points ordered 1, 2, 3 -> 1(orig 3), 2 (derived midpt of 1, 2)"

            if pointCount != 3 :
                return None, DictionaryConstants.CONVERSION_ERROR_VALIDATE_COUNT

            x0, y0 = getXYFromString(inPoints[1]) 
            x1, y1 = getXYFromString(inPoints[0]) 

            midPointX, midPointY = scale(0.5, x0, y0, x1, y1) 

            outPoints = []
            outPoints.append(inPoints[2])

            outPoints.append(getStringFromXY(midPointX, midPointY))

        msg = "Geometry Conversion: " + geoConversion
        if outPoints == None :
            msg =  "Geometry Conversion: " + geoConversion + " failed. Returning original points."
            outPoints = inPoints
            arcpy.AddWarning(msg)

            # Additional / debug info
            # print "Conversion Failed for" 
            # print sic, pointCount, geoType, geoConversion
            # print control_points
            # for key, value in attributes.items() :
            #    print key, value

        return outPoints, msg
