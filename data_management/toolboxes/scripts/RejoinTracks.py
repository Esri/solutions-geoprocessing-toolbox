#-------------------------------------------------------------------------------
# Copyright 2010-2014 Esri
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
#	Input Track Lines (FEATURELAYER)
#	Input Track Points (FEATURELAYER)
#	Field in which Track IDs are stored (FIELD)
#	Field in which start date time of track line is stored (FIELD)
#	Field in which finish date time of track line is stored (FIELD)
# OUTPUTS:
#	Output Track Lines - derived (FEATURELAYER)
#	Output Track Points - derived (FEATURELAYER)
#-------------------------------------------------------------------------------

import arcpy
from arcpy import env
import datetime
import sys

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
	desc = arcpy.Describe(inTrackLines)
	shapefieldname = desc.ShapeFieldName
	oidfieldname = desc.OIDFieldName	

	fields = shapefieldname
	if oidfieldname :
		fields += ';' + oidfieldname
	if inTrackIDField :
		fields += ';' + inTrackIDField	
	if inStartDateTimeField :
		fields += ';' + inStartDateTimeField
	if inFinishDateTimeField :
		fields += ';' + inFinishDateTimeField

	#iterate over each track line, gathering data and deleting all but the first
		
	# WARNING: Workaround encountered using this script in Pro	
	# WARNING 2: SearchCursor now also requires fields at Arcpy Pro			
	if (sys.version_info.major < 3) : 			
		updt_cursor = arcpy.UpdateCursor(inTrackLines, "", None, fields, inStartDateTimeField + ' A')
	else : 
		updt_cursor = arcpy.gp.UpdateCursor(inTrackLines, "", None, fields, inStartDateTimeField + ' A')
		
	loweststart = None
	highestfinish = None
	newtrackid = None
	changedtrackids = None
	ptarray = arcpy.Array()
	updatedLineCount = 0
	pointCount = 0
			
	for updatefeat in updt_cursor :
		updatedLineCount += 1
		startdt = updatefeat.getValue(inStartDateTimeField)
		finishdt = updatefeat.getValue(inFinishDateTimeField)
		shp = updatefeat.getValue(shapefieldname)
		polyline = shp.getPart(0)
		for pt in polyline :
			pointCount += 1
			# add the polyline to the point array that will be used to recreate a joined polyline later
			# Debug: 
			#   arcpy.AddMessage("Adding point: " + str (pointCount))
			ptarray.add(pt)
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
		
		arcpy.AddMessage("Updating track #" + str(updatedLineCount) + ", ID: " + newtrackid)
	
	#now, update the track line being left with new start and finish datetimes, and new geometry
	inFields = [inStartDateTimeField, inFinishDateTimeField, "SHAPE@"]
	linecursor = arcpy.da.UpdateCursor(inTrackLines, inFields)
	
	if linecursor is None :
		arcpy.AddError("Could not obtain update cursor on " + str(inTrackLines))
	
	ft = next(linecursor)
	
	arcpy.AddMessage("Resetting times/values for next track.")	
	if ft is not None :
		ft[0] = loweststart
		ft[1] = highestfinish
		#Debug:
		# arcpy.AddMessage("Resetting shape for next track. Shape field: " + shapefieldname)	
		# if pointCount != ptarray.count :
		#	arcpy.AddMessage("Shape has unexpected point count: " + str(pointCount) + " vs. " + str(ptarray.count))
		try : 
			outPoly = arcpy.Polyline(ptarray)
			ft[2] = outPoly
		except Exception as err:
			import traceback
			arcpy.AddError(traceback.format_exception_only(type(err), err)[0].rstrip())
		
		linecursor.updateRow(ft)

	#finally, update all points with the Track IDs affected to the new Track ID
	arcpy.AddMessage("Updating track points where " + changedtrackids)
	if (sys.version_info.major < 3) : 		
		ptcursor = arcpy.UpdateCursor(inTrackPoints, changedtrackids)
	else : 
		ptcursor = arcpy.gp.UpdateCursor(inTrackPoints, changedtrackids)

	for feat in ptcursor :
		feat.setValue(inTrackIDField, newtrackid)
		ptcursor.updateRow(feat)
			
	arcpy.SetParameterAsText(5, inTrackLines)
	arcpy.SetParameterAsText(6, inTrackPoints)

except Exception as err :
	import traceback
	arcpy.AddError(traceback.format_exception_only(type(err), err)[0].rstrip())

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
