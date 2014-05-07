#--------ESRI 2010-------------------------------------
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
# Calculate Field DeltaTime
# This script will calculate the time spent around a point
# in a GPS track series as half the timespan between the 2
# points either side and will add that time in seconds to
# a numeric field, the name of which is passed as a parameter.
# Each track (as identified in the Track ID Field) will be
# treated separately
# INPUTS: 
#    GPS Track Points (FEATURECLASS)
#    DateTime Field (FIELD)
#    Field in which to store time spent (FIELD)
#    Track ID Field (FIELD)
# OUTPUTS:
#    GPS Track Points - derived (FEATURECLASS)
# 
# Date: June 30, 2010
#------------------------------------------------------

import arcpy
import datetime, time

try:
    #set features and cursors so that they are deletable in
    #'finally' block should the script fail prior to their creation
    nextfeat, srch_cursor = None, None
    updatefeat, updt_cursor = None, None

    inPoints = arcpy.GetParameterAsText(0)
    inDateField = arcpy.GetParameterAsText(1)
    inDeltaTimeField = arcpy.GetParameterAsText(2)
    inTrackIDField = arcpy.GetParameterAsText(3)
   
    srch_cursor = arcpy.SearchCursor(inPoints,"",None,"",inDateField + " A")
    nextfeat = srch_cursor.next()
    nextfeat = srch_cursor.next() # this cursor looks at the point after the one being updated
    updt_cursor = arcpy.UpdateCursor(inPoints,"",None,"",inDateField + " A")
    updatefeat = updt_cursor.next()

    lastdt = None
    lastid, thisid, nextid = None, None, None
    
    while updatefeat:
        thisdt = updatefeat.getValue(inDateField)
        if inTrackIDField:
            thisid = updatefeat.getValue(inTrackIDField)
            if thisid != lastid:
                lastdt = None
        if nextfeat:
            if inTrackIDField:
                nextid = nextfeat.getValue(inTrackIDField)
            if thisid == nextid:
                nextdt = nextfeat.getValue(inDateField)
            else:
                nextdt = None
        else:
            nextdt = None
        if lastdt:
            if nextdt:
                span = (nextdt - lastdt)
            else:
                span = (thisdt - lastdt)
        else:
            if nextdt:
                span = (nextdt - thisdt)
            else:
                span = None
        if span:
            span = float(span.seconds) / 2
            updatefeat.setValue(inDeltaTimeField, span)
            updt_cursor.updateRow(updatefeat)

        lastid = thisid
        lastdt = thisdt
        updatefeat = updt_cursor.next()        
        if updatefeat:
            nextfeat = srch_cursor.next()

    arcpy.SetParameterAsText(4, inPoints)

except:
    if not arcpy.GetMessages() == "":
        arcpy.AddMessage(arcpy.GetMessages(2))

finally:
    if nextfeat:
        del nextfeat
    if srch_cursor:
        del srch_cursor
    if updatefeat:
        del updatefeat
    if updt_cursor:
        del updt_cursor
