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
# MilitaryUtilities.py
# Description: Miscellaneous shared objects and methods
#----------------------------------------------------------------------------------

import sqlite3
import uuid
import re
import arcpy
import os
import SymbolDictionary
import GeometryConverter
import DictionaryConstants

# All Paths used/shared by the scripts are here:
currentPath = os.path.dirname(__file__)
dataPath = os.path.normpath(os.path.join(currentPath, r"../../data/"))
# IMPORTANT: assumes Mil2525C.dat is at ../../data/dictionary
dictionaryPath2525 = os.path.normpath(os.path.join(dataPath, r"mil2525c/dictionary/"))
dictionaryPathApp6 = os.path.normpath(os.path.join(dataPath, r"app6b/dictionary/"))
symbolDictionaryPath2525 = os.path.join(dictionaryPath2525,  "Mil2525C.dat" )
symbolDictionaryPathAPP6 = os.path.join(dictionaryPathApp6,  "App6b.dat" )
symbolDictionaryPath = None

def setSymbologyStandard(standard) :
    
    global symbolDictionary, symbolDictionaryPath, symbolDictionaryPath2525, \
        symbolDictionaryPathAPP6
    
    if (standard is None) or (standard == "") : 
        print "WARNING: standard is null, using default"
        symbolDictionaryPath = symbolDictionaryPath2525
        return    
    
    if standard.upper().find("APP6") >= 0 :
        symbolDictionaryPath = symbolDictionaryPathAPP6
    else : 
        symbolDictionaryPath = symbolDictionaryPath2525
        
    return
    
def getSymbolDictionary() :
    
    global symbolDictionary, symbolDictionaryPath, symbolDictionaryPath2525
    
    try :
    
        if (symbolDictionaryPath is None) : 
            print "WARNING: SymbologyStandard / SymbolDictionaryPath has not been set, using default"
            symbolDictionaryPath = symbolDictionaryPath2525
        
        if symbolDictionary is None :         
            print "Creating Dictionary from: " +  symbolDictionaryPath
            symbolDictionary = SymbolDictionary.SymbolDictionary(symbolDictionaryPath)
        
    except :
        print "Exception in getSymbolDictionary"    
        
    return symbolDictionary

def getSymbolDictionaryStandard(standard) :
    
    setSymbologyStandard(standard)    
    return getSymbolDictionary()
        
def getGeometryConverter() :
 
    global geoConverter, symbolDictionary, symbolDictionaryPath, symbolDictionaryPath2525
    
    try :
   
        if (symbolDictionaryPath is None) : 
            print "WARNING: SymbologyStandard / SymbolDictionaryPath has not been set, using default"
            symbolDictionaryPath = symbolDictionaryPath2525
                
        if geoConverter is None : 
            print "Creating GeometryConverter from: " +  symbolDictionaryPath  
            getSymbolDictionary()
            geoConverter = GeometryConverter.GeometryConverter(symbolDictionary)
        
    except :
        print "Exception in getGeometryConverter"            
              
    return geoConverter
        
def getGeometryConverterStandard(standard) :
    
    setSymbologyStandard(standard)    
    return getGeometryConverter()
        
# Some common helper objects
## WARNING: these will not be initialized until getSymbolDictionary / getGeometryConverter
## are called, this lazy initialization is needed to allow the Symbol Standard to 
## be set before creation

## TODO: may want to make these private/mangled names (prefix with "__")
symbolDictionary = None # SymbolDictionary.SymbolDictionary(symbolDictionaryPath)
geoConverter = None # GeometryConverter.GeometryConverter(symbolDictionary)

# Some Military Feature Fields  
MessageTypeField = "messagetype"
UniqueDesignationField = "UniqueDesignation"
SidcFieldChoice1 = "sic"
SidcFieldChoice2 = "sidc"

##########################################################
# Getter Methods, just in case tag name changes 
def getBaseMessageTag() : 
    return DictionaryConstants.MessageTagName    # geomessage

def getMessageRootTag():        
    return getBaseMessageTag() + "s" # ex: "geomessages"
    
def getMessageTag():        
    return getBaseMessageTag() # ex: "geomessage"
    
def getMessageVersion():        
    return DictionaryConstants.MessageVersion    # ex. 1.0 
##########################################################

##########################################################
# Handles Common geometry list conversions

def pointsToArcPyGeometry(pointList, shapeType) : 

    arcPoint = arcpy.Point()
    arcArray = arcpy.Array()
       
    for point in pointList : 
        x = point.split(',')[0]
        y = point.split(',')[1]
        # print "(", x, ",", y, ")"
        arcPoint.X = float(x)
        arcPoint.Y = float(y)
        arcArray.add(arcPoint)

    if shapeType == "Point" : 
        return arcPoint
    elif shapeType == "Polyline" : 
        arcPolyline = arcpy.Polyline(arcArray)
        return arcPolyline
    elif shapeType == "Polygon" : 
        arcPolygon = arcpy.Polygon(arcArray)
        return arcPolygon
              
def parsePartToControlPoints(part):
    controlPoints = ""
    sep = ""
    
    try :
    
        for subpart in part:
            try:
                # assume it's a point
                subpartStr = str(subpart.X) + "," + str(subpart.Y)
                controlPoints = controlPoints + sep + subpartStr
                sep = ";"
            except AttributeError:
                # it's an array of parts, i.e. a part
                controlPoints = controlPoints + sep + parsePartToControlPoints(subpart)
                sep = ";"
                                
    except :
        print "Exception in parsePartToControlPoints"   
            
    return controlPoints

def parseGeometryToControlPoints(geom):
    try:
        # assume it's a point
        return str(geom.X) + "," + str(geom.Y)
    except AttributeError:
        # it's not a point
        try:
            controlPoints = ""
            sep = ""
            for i in range(geom.partCount):
                part = geom.getPart(i)
                # part is an array
                for subpart in part:
                    controlPoints = controlPoints + sep + parsePartToControlPoints(part)
                    sep = ";"
            return controlPoints
        except AttributeError:
            # it's a part
            return parsePartToControlPoints(geom)
             
def reverseControlPoints(string):
    revnums = re.split(r'(\;+)', string)
    revnums.reverse()
    revnums = ''.join(revnums)
    return revnums
