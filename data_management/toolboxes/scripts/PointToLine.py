#-------------------------------------------------------------------------------
# Copyright 2010-2013 Esri
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
#-------------------------------------------------------------------------------
# PointToLine.py
# Description: Convert set of feature points to line
# Requirements: ArcGIS Desktop Standard
# ------------------------------------------------------------------------------

import os
import types
import arcpy

def convertPoints():
    
    overwriteOutputDefault = arcpy.overwriteOutput
    arcpy.overwriteOutput = True

    # Input point FC
    # Output FC
    # Feature Field
    # Sort Field
    # Close Line or Leave Open
    inPts       = arcpy.GetParameterAsText(0)
    outFeatures = arcpy.GetParameterAsText(1)
    IDField     = arcpy.GetParameterAsText(2)
    sortField   = arcpy.GetParameterAsText(3)
    closeLine   = arcpy.GetParameterAsText(4)

    if IDField in ["", "#"]:
        IDField = None

    if sortField in ["", "#"]:
        cursorSort = IDField
    else:
        if IDField:
            cursorSort = IDField + ";" + sortField
        else:
            cursorSort = sortField

    if types.TypeType(closeLine) != types.BooleanType:
        if closeLine.lower() == "false":
            close = False
        else:
            close = True

    convertPointsToLine(inPts, outFeatures, IDField, cursorSort, close)
    arcpy.overwriteOutput = overwriteOutputDefault

def enableParam(hasMZ):
    if hasMZ:
        return "ENABLED"
    else:
        return "DISABLED"       

def convertPointsToLine(inPts, outFeatures, IDField, cursorSort, close):
    try:
        # Assign empty values to cursor and row objects
        iCur, sRow, sCur, feat = None, None, None, None

        desc = arcpy.Describe(inPts)
        shapeName = desc.shapeFieldName

        # Create the output feature class
        #
        outPath, outFC = os.path.split(outFeatures)
        arcpy.CreateFeatureclass_management(outPath, outFC, "POLYLINE", "",
                                         enableParam(desc.hasM),
                                         enableParam(desc.hasZ),
                                         inPts)

        # If there is an IDField, add the equivalent to the output
        #
        if IDField:
            f = arcpy.ListFields(inPts, IDField)[0]
            tMap = {'Integer': 'LONG', 'String': 'TEXT', 'SmallInteger': 'SHORT'}
            fType = f.type
            if tMap.has_key(fType):
                fType = tMap[fType]
            fName = arcpy.ValidateFieldName(f.name, outPath)
            arcpy.AddField_management(outFeatures, fName, fType, f.precision, f.scale, f.length,
                                   f.aliasName, f.isNullable, f.required, f.domain)

        # Open an insert cursor for the new feature class
        #
        iCur = arcpy.InsertCursor(outFeatures)
        sCur = arcpy.SearchCursor(inPts, "", None, cursorSort, cursorSort)

        sRow = sCur.Next()

        # Create an array and point object needed to create features
        #
        array = arcpy.CreateObject("Array")
        pt = arcpy.CreateObject("Point")

        # Initialize a variable for keeping track of a feature's ID.
        #
        ID = -1
        while sRow:
            pt = sRow.getValue(shapeName).getPart(0)
            if IDField: 
                currentValue = sRow.getValue(IDField)
            else:
                currentValue = None

            if ID == -1:
                ID = currentValue

            if ID <> currentValue:
                if array.count >= 2:
                                        
                    # To close, add first point to the end
                    #
                    if close:
                        array.add(array.getObject(0))
                    
                    feat = iCur.newRow()
                    if IDField:
                        if ID: #in case the value is None/Null
                            feat.setValue(IDField, ID)
                    feat.setValue(shapeName, array)
                    iCur.insertRow(feat)
                else:
                    arcpy.AddIDMessage("WARNING", 1059, str(ID))
                                  
                array.removeAll()

            array.add(pt)
            ID = currentValue
            sRow = sCur.next()

        # Add the last feature
        #
        if array.count > 1:
            # To close, add first point to the end
            #
            if close:
                array.add(array.getObject(0))
                                
            feat = iCur.newRow()
            if IDField:
                if ID: #in case the value is None/Null
                    feat.setValue(IDField, currentValue)
            feat.setValue(shapeName, array)
            iCur.insertRow(feat)
        else:
            arcpy.AddIDMessage("WARNING", 1059, str(ID))
        array.removeAll()

    except Exception as err:
        arcpy.AddError(err.message)

    finally:
        if iCur:
            del iCur
        if sRow:
            del sRow
        if sCur:
            del sCur
        if feat:
            del feat

if __name__ == '__main__':
    convertPoints()
    
