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
# Calculate Field FloatDate
# This script will calculate the Unix timestamp of a date
# field and populate a 'FloatDate' field with the result
# INPUTS:
#	Input Table (TABLE)
#	DateTime Field (FIELD)
#	Field in which to store FloatDate (FIELD)
# OUTPUTS:
#	Output Table - derived (TABLE)
#
# Date: June 30, 2010
#------------------------------------------------------

import sys
import arcpy
import datetime, time
from time import mktime

try:
	#set features and cursors so that they are deletable in
	#'finally' block should the script fail prior to their creation
	updatefeat, updt_cursor = None, None

	inTable = arcpy.GetParameterAsText(0)
	inDateField = arcpy.GetParameterAsText(1)
	inFloatDateField = arcpy.GetParameterAsText(2)

	fields = inDateField + ';' + inFloatDateField
	
	if (sys.version_info.major < 3) : 	
		updt_cursor = arcpy.UpdateCursor(inTable, "", None, fields, inDateField + " A")
	else : 
		updt_cursor = arcpy.gp.UpdateCursor(inTable, "", None, fields, inDateField + " A")
		
	for updatefeat in updt_cursor :
		dt = updatefeat.getValue(inDateField)
		floatdate = mktime(dt.timetuple()) + 1e-6*dt.microsecond
		updatefeat.setValue(inFloatDateField, floatdate)
		updt_cursor.updateRow(updatefeat)

	arcpy.SetParameterAsText(3, inTable)

except Exception as err:
	import traceback
	arcpy.AddError(traceback.format_exception_only(type(err), err)[0].rstrip())

finally:
	if updatefeat:
		del updatefeat
	if updt_cursor:
		del updt_cursor
