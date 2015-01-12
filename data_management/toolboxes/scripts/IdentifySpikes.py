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
# Identify GPS Spikes
# This script looks at distances and bearings
# between points in a featureclass and, given
# a max distance value and max deviation,
# identifies potential spikes (exceeding both
# max values)
# INPUTS:
#	Input Points Feature Class (FEATURECLASS)
#	Distance Field - holding dist from last point to this (FIELD)
#	Bearing Field - holding deviation around this point (FIELD)
#	DateTime Field - holding the GPS Timestamp (FIELD)
#	Spike Field - this script will set it to 'True' for spikes (FIELD)
#	Maximum Distance - value above which points are considered potential spikes (DOUBLE)
#	Maximum Deviation - value above which points are considered potential spikes (DOUBLE)
# OUTPUTS:
#	Output Points (DERIVED FEATURECLASS)
#-------------------------------------------------------------------------------

import arcpy
import time
import datetime
import math

try:
	#set features and cursors so that they are deletable in
	#'finally' block should the script fail prior to their creation
	feature, features, nextfeature, findfeatures = None, None, None, None
	distanceval = None
	bearingval = None

	points = arcpy.GetParameterAsText(0)
	distancefield = arcpy.GetParameterAsText(1)
	bearingfield = arcpy.GetParameterAsText(2)
	datetimefield = arcpy.GetParameterAsText(3)
	spikefield = arcpy.GetParameterAsText(4)
	maxdistance = arcpy.GetParameterAsText(5)
	maxdeviation = arcpy.GetParameterAsText(6)

	maxdistance = float(maxdistance)
	maxdeviation = float(maxdeviation)

	fields = datetimefield
	if distancefield :
		fields += ';' + distancefield
	if bearingfield :
		fields += ';' + bearingfield
	if spikefield :
		fields += ';' + spikefield
		
	# WARNING: Workaround encountered using this script in Pro	
	# WARNING 2: SearchCursor now also requires fields at Arcpy Pro			
	if (sys.version_info.major < 3) : 			
		features = arcpy.UpdateCursor(points, "", None, fields, datetimefield + " A")
		findfeatures = arcpy.SearchCursor(points, "", None, fields, datetimefield + " A")
	else : 
		features = arcpy.gp.UpdateCursor(points, "", None, fields, datetimefield + " A")
		findfeatures = arcpy.gp.SearchCursor(points, "", None, fields, datetimefield + " A")
	
	feature= next(features)
	nextfeature = next(findfeatures)

	try : 
	
		while feature:
			nextfeature = next(findfeatures)
			distanceval = feature.getValue(distancefield)
			bearingval = feature.getValue(bearingfield)
			feature.setValue(spikefield, "false")
			if (distanceval > maxdistance):
				#unusually high distance - could be a spike if it's the last point or if the next point also shows a high distance (returning from the outlier)
				if nextfeature:
					nextdistanceval = nextfeature.getValue(distancefield)
				else:
					nextdistanceval = distanceval
				if (nextdistanceval > maxdistance):
					#2 high distances in a row, suggests out and back from a spike so check for accompanying change in deviation
					if nextfeature:
						nextbearingval = nextfeature.getValue(bearingfield)
						deviation = math.fabs(nextbearingval - bearingval)
						if (deviation > maxdeviation) and ((360 - deviation) > maxdeviation):
							feature.setValue(spikefield, "true")
			features.updateRow(feature)
			feature = next(features)
		
	except StopIteration:
		pass	# this is expected for iterators that use next()		

	arcpy.SetParameterAsText(7, points)

except Exception as err :
	import traceback
	arcpy.AddError(traceback.format_exception_only(type(err), err)[0].rstrip())

finally:
	if feature:
		del feature
	if features:
		del features
	if nextfeature:
		del nextfeature
	if findfeatures:
		del findfeatures
