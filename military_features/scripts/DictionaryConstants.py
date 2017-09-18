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
# DictionaryConstants.py
# Description: Shared constants
#----------------------------------------------------------------------------------

# Message Processor Tags
MessageTagName = "geomessage"
MessageVersion = "1.0"

DefaultMessageType = "position_report"
DefaultMessageAction = "update"

Tag_ControlPoints = "_control_points"
Tag_SymbolId      = "sic"
Tag_Wkid          = "_wkid"
Tag_Id            = "_id"
Tag_Radius        = "Radius"
Tag_Length        = "Length"
Tag_Width         = "Width"
Tag_Orientation   = "Orientation"
Tag_UniqueDesignation = "uniquedesignation"
Tag_TwoLinesNeeded= "TWOLINES"

MESSAGES_TAG_LIST = [Tag_ControlPoints, Tag_SymbolId, Tag_Wkid, Tag_Id, Tag_Radius, Tag_Length, \
                        Tag_Width, Tag_Orientation, Tag_TwoLinesNeeded, Tag_UniqueDesignation ]

RuleFieldsList = { "ruleid", "symbolrule" }

FRIENDLY_AFFILIATION = "FRIENDLY"
HOSTILE_AFFILIATION  = "HOSTILE"
NEUTRAL_AFFILIATION  = "NEUTRAL"
UNKNOWN_AFFILIATION  = "UNKNOWN"

validAffiliations = { FRIENDLY_AFFILIATION, HOSTILE_AFFILIATION, NEUTRAL_AFFILIATION, UNKNOWN_AFFILIATION } 

affiliationToAffiliationChar = dict([ \
            (FRIENDLY_AFFILIATION, 'F'), \
            (HOSTILE_AFFILIATION, 'H'), \
            (NEUTRAL_AFFILIATION, 'N'), \
            (UNKNOWN_AFFILIATION, 'U')])

UNKNOWN_GEOMETRY_STRING     = "Unknown"
POINT_STRING                = "Point"
LINE_STRING                 = "Line"
AREA_STRING                 = "Area"
GEOMETRY_STRING             = "Geometry"

DEFAULT_POINT_SIDC = "SUGPU----------"
DEFAULT_LINE_SIDC  = "GUGPGLB-------X"
DEFAULT_AREA_SIDC  = "GUGPGAG-------X"

CONVERSION_ERROR_VALIDATION      = "Validation FAILED"
CONVERSION_ERROR_VALIDATE_COUNT  = "Validation FAILED - Unexpected Point Count"
CONVERSION_ERROR_VALIDATE_RADIUS = "Validation FAILED - Radius <= 0"
CONVERSION_IGNORE_SECOND_LINE    = "Ignoring Second Part"

GCT_POINT                 	= "GCT_Point"
GCT_POLYLINE            	= "GCT_Polyline"
GCT_POLYGON               	= "GCT_Polygon"
GCT_INDETERMINATE     	 	= "GCT_Indeterminate"
GCT_ARROW                 	= "GCT_Arrow"
GCT_ARROWWITHOFFSET    	    = "GCT_ArrowWithOffset"
GCT_ARROWWITHTAIL     	 	= "GCT_ArrowWithTail"
GCT_CIRCLE					= "GCT_Circle"
GCT_CIRCULAR            	= "GCT_Circular"
GCT_FREEHANDARROW			= "GCT_FreehandArrow"
GCT_FREEHANDLINE          	= "GCT_FreehandLine"
GCT_FREEHANDREVERSEARROW 	= "GCT_FreehandReverseArrow"
GCT_FREEHANDU           	= "GCT_FreehandU"
GCT_HOOK                  	= "GCT_Hook"
GCT_HORNS					= "GCT_Horns"
GCT_OPENTRIANGLE			= "GCT_OpenTriangle"
GCT_PARALLELLINES			= "GCT_ParallelLines"
GCT_PARALLELLINESMIDLINE 	= "GCT_ParallelLinesMidline"
GCT_PARALLELLINESWITHTICKS  = "GCT_ParallelLinesWithTicks"
GCT_RECTANGULAR         	= "GCT_Rectangular"
GCT_RECTANGULAR1PT       	= "GCT_Rectangular1Pt"
GCT_T                     	= "GCT_T"
GCT_TRIPLEARROW        	    = "GCT_TripleArrow"
GCT_TWOLINE              	= "GCT_TwoLine"
GCT_TWOLINE3OR4PT        	= "GCT_TwoLine3Or4Pt"
GCT_UORTSHAPE           	= "GCT_UOrTShape"

# Exclude these fields from copy/updates
MILFEATURES_FIELD_EXCLUDE_LIST = ["shape", "Shape", "SHAPE", "objectid", "sort", "OBJECTID",\
    "messagetype", "sidc", "createdby", "editedby", "createdtime", "editedtime", "override",\
    "shape_Length", "shape_Area", "SHAPE_Length", "SHAPE_Area", "Shape_Length", "Shape_Area",\
    "ruleid", "symbolrule" ]

def getGeometryStringFromShapeType(shapeType) :
    if shapeType == "Point" : 
        return POINT_STRING
    elif shapeType == "Polyline" :
        return LINE_STRING         
    elif shapeType == "Polygon" : 
        return AREA_STRING
    else :
        return POINT_STRING

def getDefaultSidcForGeometryString(geoString) : 
    if geoString == POINT_STRING  : 
        return DEFAULT_POINT_SIDC
    elif geoString == LINE_STRING :
        return DEFAULT_LINE_SIDC         
    elif geoString == AREA_STRING : 
        return DEFAULT_AREA_SIDC
    else :
        return DEFAULT_POINT_SIDC

def getDefaultSidcForShapeType(shapeType) : 
    if shapeType == "Point" : 
        return DEFAULT_POINT_SIDC
    elif shapeType == "Polyline" :
        return DEFAULT_LINE_SIDC         
    elif shapeType == "Polygon" : 
        return DEFAULT_AREA_SIDC
    else :
        return DEFAULT_POINT_SIDC

def isCorrectShapeTypeForFeature(geoType, shapeType) :
    if (geoType == POINT_STRING) and (shapeType == "Point") : 
        return True
    elif (geoType == LINE_STRING) and (shapeType == "Polyline") : 
        return True
    elif (geoType == AREA_STRING) and (shapeType == "Polygon") : 
        return True
    else :
        return False
