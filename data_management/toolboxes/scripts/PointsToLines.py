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
# Points to Lines
# This script takes a set of points, sorts them by
# a specified field, and splits them by a 'line identity'
# field in order to then create a set of lines in the
# specified line feature class that correspond to the
# point features. This was built specifically for the
# purpose of converting GPS track points to track lines.
# INPUTS:
#	Input Points Feature Class (FEATURE LAYER)
#	Output Line Feature Class (FEATURE LAYER)
#	ID Field - holding an ID that identifies the points as belonging to unique lines (FIELD)
#	Sort Field - describing how to sort the points prior to generating lines from them
# OUTPUTS:
#	Output Lines (DERIVED FEATURECLASS)
#-------------------------------------------------------------------------------

import arcpy
import os

inPts = arcpy.GetParameterAsText(0)
outFeatures = arcpy.GetParameterAsText(1)
IDField = arcpy.GetParameterAsText(2)
sortField = arcpy.GetParameterAsText(3)

if sortField:
	if IDField:
		cursorSort = IDField + " A;" + sortField  + " A"
	else:
		cursorSort = sortField + " A"
else:
	cursorSort = IDField + " A"

try:
	# Assign empty values to array, cursor and row objects
	array, iCur, sRow, sCur, feat = None, None, None, None, None

	desc = arcpy.Describe(inPts)
	shapeName = desc.shapeFieldName

	# Open an insert cursor for the new feature class
	iCur = arcpy.InsertCursor(outFeatures)

	# Create an array and point object needed to create features
	#
	array = arcpy.Array()
	pt = arcpy.Point()

	# Initialize a variable for keeping track of a feature's ID.
	#

	ID = -1
	fields = shapeName
	if IDField :
		fields += ";" + IDField
	if sortField :
		fields += ";" + sortField

	for sRow in arcpy.gp.SearchCursor(inPts, "", None, fields, cursorSort) :

		f = sRow.getValue(shapeName)
		
		if (f is None) :
			arcpy.AddError('Could not read shape field: ' + shapeName)
			continue
		
		pt = f.getPart(0)

		if IDField: currentValue = sRow.getValue(IDField)

		else: currentValue = None

		if ID == -1: ID = currentValue

		if ID != currentValue:
			if array.count >= 2:
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

	# Add the last feature
	#
	if array.count > 1:
		feat = iCur.newRow()
		if IDField:
			if ID: #in case the value is None/Null
				feat.setValue(IDField, currentValue)
		feat.setValue(shapeName, array)
		iCur.insertRow(feat)
	else:
		arcpy.AddIDMessage("WARNING", 1059, str(ID))
		
	array.removeAll()

	arcpy.SetParameterAsText(4, outFeatures)

except Exception as err:
	import traceback
	arcpy.AddError(
		traceback.format_exception_only(type(err), err)[0].rstrip())

finally:
	if array:
		del array
	if iCur:
		del iCur
	if sRow:
		del sRow
	if sCur:
		del sCur
	if feat:
		del feat
