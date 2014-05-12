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
# Rejoin tracks
# This script will take any number of tracks selected in
#'inTrackLines' and condense them to one track, updating
# all the associated points to the new single track id
# INPUTS: 
#    Input Track Lines (FEATURELAYER)
#    Input Track Points (FEATURELAYER)
#    Field in which Track IDs are stored (FIELD)
#    Field in which start date time of track line is stored (FIELD)
#    Field in which finish date time of track line is stored (FIELD)
# OUTPUTS:
#    Output Track Lines - derived (FEATURELAYER)
#    Output Track Points - derived (FEATURELAYER)
#-------------------------------------------------------------------------------

import arcpy
from arcpy import env
import datetime

env.overwriteOutput = True

try:
    #set features and cursors so that they are deletable in
    #'finally' block should the script fail prior to their creation
    updatefeat, updt_cursor = None, None
    ft, linecursor = None, None
    feat, ptcursor = None, None

    inTrackLines = arcpy.GetParameterAsText(0)
    inTrackPoints = arcpy.GetParameterAsText(1)
    inTrackIDField = arcpy.GetParameterAsText(2)
    inStartDateTimeField = arcpy.GetParameterAsText(3)
    inFinishDateTimeField = arcpy.GetParameterAsText(4)

    #we'll need to join the lines, so get the shape field name
    #desc = arcpy.Describe(inTrackLines)
    #shapefieldname = desc.ShapeFieldName

    #iterate over each track line, gathering data and deleting all but the first    
    updt_cursor = arcpy.UpdateCursor(inTrackLines,"",None,"",inStartDateTimeField)
    updatefeat = updt_cursor.next()

    loweststart = None
    highestfinish = None
    newtrackid = None
    changedtrackids = None
    ptarray = arcpy.Array()
    
    while updatefeat:
        startdt = updatefeat.getValue(inStartDateTimeField)
        finishdt = updatefeat.getValue(inFinishDateTimeField)
        shp = updatefeat.shape
        polyline = shp.getPart(0)
        pt = polyline.next()
        while pt:
            #add the polyline to the point array that will be used to recreate a joined polyline later
            ptarray.add(pt)
            pt = polyline.next()
        if loweststart:
            if startdt < loweststart:
                loweststart = startdt
        else:
            loweststart = startdt
        if highestfinish:
            if finishdt > highestfinish:
                highestfinish = finishdt
        else:
            highestfinish = finishdt
            
        if newtrackid:
            if changedtrackids:
                changedtrackids += " OR \"" + inTrackIDField + "\" = '" + updatefeat.getValue(inTrackIDField) + "'"
            else:
                changedtrackids = "\"" + inTrackIDField + "\" = '" + updatefeat.getValue(inTrackIDField) + "'"
            updt_cursor.deleteRow(updatefeat)
        else:
            newtrackid = updatefeat.getValue(inTrackIDField)
        updatefeat = updt_cursor.next()

    #now, update the track line being left with new start and finish datetimes, and new geometry
    linecursor = arcpy.UpdateCursor(inTrackLines)
    ft = linecursor.next()
    ft.setValue(inStartDateTimeField, loweststart)
    ft.setValue(inFinishDateTimeField, highestfinish)
    ft.shape = ptarray
    linecursor.updateRow(ft)

    #finally, update all points with the Track IDs affected to the new Track ID
    arcpy.AddMessage("update track points where " + changedtrackids)
    ptcursor = arcpy.UpdateCursor(inTrackPoints,changedtrackids)
    feat = ptcursor.next()

    while feat:
        feat.setValue(inTrackIDField, newtrackid)
        ptcursor.updateRow(feat)
        feat = ptcursor.next()
    
    arcpy.SetParameterAsText(5, inTrackLines)
    arcpy.SetParameterAsText(6, inTrackPoints)

except:
    if not arcpy.GetMessages() == "":
        arcpy.AddMessage(arcpy.GetMessages(2))

finally:
    if updatefeat:
        del updatefeat
    if updt_cursor:
        del updt_cursor
    if ft:
        del ft
    if linecursor:
        del linecursor
    if feat:
        del feat
    if ptcursor:
        del ptcursor



