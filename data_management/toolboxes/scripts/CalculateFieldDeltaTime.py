#--------ESRI 2010-------------------------------------
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
# Calculate Field DeltaTime
# This script will calculate the time spent around a point
# in a GPS track series as half the timespan between the 2
# points either side and will add that time in seconds to
# a numeric field, the name of which is passed as a parameter.
# Each track (as identified in the Track ID Field) will be
# treated separately
# INPUTS:
#	GPS Track Points (FEATURECLASS)
#	DateTime Field (FIELD)
#	Field in which to store time spent (FIELD)
#	Track ID Field (FIELD)
# OUTPUTS:
#	GPS Track Points - derived (FEATURECLASS)
#
# Date: June 30, 2010
#------------------------------------------------------

import arcpy
import datetime
import sys
import time

try:
	#set features and cursors so that they are deletable in
	#'finally' block should the script fail prior to their creation
	nextfeat, srch_cursor = None, None
	updatefeat, updt_cursor = None, None

	inPoints = arcpy.GetParameterAsText(0)
	inDateField = arcpy.GetParameterAsText(1)
	inDeltaTimeField = arcpy.GetParameterAsText(2)
	inTrackIDField = arcpy.GetParameterAsText(3)

	fields = inDateField + ';' + inDeltaTimeField
	if inTrackIDField :
		fields += ';' + inTrackIDField
		
	# WARNING: Workaround encountered using this script in Pro	
	# WARNING 2: SearchCursor now also requires fields at Arcpy Pro	
	if (sys.version_info.major < 3) : 
		srch_cursor = arcpy.SearchCursor(inPoints, "", None, fields, inDateField + " A")
	else : 
		srch_cursor = arcpy.gp.SearchCursor(inPoints, "", None, fields, inDateField + " A")
	
	nextfeat = next(srch_cursor)
	nextfeat = next(srch_cursor) # this cursor looks at the point after the one being updated
	
	# WARNING: Workaround encountered using this script in Pro
	if (sys.version_info.major < 3) : 
		updt_cursor = arcpy.UpdateCursor(inPoints, "", None, fields, inDateField + " A")
	else :
		updt_cursor = arcpy.gp.UpdateCursor(inPoints, "", None, fields, inDateField + " A")
	
	updatefeat = next(updt_cursor)

	lastdt = None
	lastid, thisid, nextid = None, None, None

	try : 
	
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
			updatefeat = next(updt_cursor)
			if updatefeat:
				nextfeat = next(srch_cursor)
	except StopIteration:
		pass	# this is expected for iterators that use next()

	arcpy.SetParameterAsText(4, inPoints)

except Exception as err:
	import traceback
	arcpy.AddError(
		traceback.format_exception_only(type(err), err)[0].rstrip())

finally:
	if nextfeat:
		del nextfeat
	if srch_cursor:
		del srch_cursor
	if updatefeat:
		del updatefeat
	if updt_cursor:
		del updt_cursor
