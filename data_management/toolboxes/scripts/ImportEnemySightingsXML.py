# Enemy Sightings (from XML) to Table
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
# This script will take an XML file representing
# a completed InfoPath Patrol Report and
# add the 'EnemySightings' elements as a row(s) to
# an ArcGIS Table of identical schema, against
# the specified Track ID
# INPUTS:
#    XML file (FILE)
#    Track ID (STRING)
# OUTPUTS:
#    Output Table (TABLE)
#-------------------------------------------------------------------------------

from xml.etree import ElementTree
from datetime import datetime
import arcpy, string
import re

def enemysightingstodict(xmlfile):
	''' Parses the xml to extract the EnemySightings fields into a dictionary '''

	PATROLREPORT_NS = '{http://helyx.co.uk/infopath/2003/myXSD/2010-06-09}'

	tree = ElementTree.parse(xmlfile)

	for node in tree.findall(PATROLREPORT_NS + 'Observations/' + PATROLREPORT_NS + 'EnemySightings'):
		d = {}
		''' get each of the nodes '''
		datetimesighted = node.find(PATROLREPORT_NS + 'DateTimeSighted').text
		strength = node.find(PATROLREPORT_NS + 'Strength').text
		activityattitude = node.find(PATROLREPORT_NS + 'ActivityAttitude').text
		weaponsequipment = node.find(PATROLREPORT_NS + 'WeaponsEquipment').text
		disposition = node.find(PATROLREPORT_NS + 'Disposition').text
		intention = node.find(PATROLREPORT_NS + 'Intention').text
		additionalobservations = node.find(PATROLREPORT_NS + 'AdditionalObservations').text

		yield datetimesighted, strength, activityattitude, weaponsequipment, \
			  disposition, intention, additionalobservations

def parse_timestamp(s):
	''' Returns (datetime, tz offset in minutes) or (None, None). '''
	m = re.match(""" ^
	(?P<year>-?[0-9]{4}) - (?P<month>[0-9]{2}) - (?P<day>[0-9]{2})
	T (?P<hour>[0-9]{2}) : (?P<minute>[0-9]{2}) : (?P<second>[0-9]{2})
	(?P<microsecond>\.[0-9]{1,6})?
	(?P<tz>
	  Z | (?P<tz_hr>[-+][0-9]{2}) : (?P<tz_min>[0-9]{2})
	)?
	$ """, s, re.X)

	if m is not None:
		values = m.groupdict()
		
	if values["tz"] in ("Z", None):
		tz = 0
	else:
		tz = int(values["tz_hr"]) * 60 + int(values["tz_min"])
		
	if values["microsecond"] is None:
		values["microsecond"] = 0
	else:
		values["microsecond"] = values["microsecond"][1:]
		values["microsecond"] += "0" * (6 - len(values["microsecond"]))

	values = dict((k, int(v)) for k, v in list(values.items())
		if not k.startswith("tz"))
	try:
		return datetime(**values), tz
	except ValueError:
		pass
		
	return None, None

if __name__ == "__main__":

	xmlfile = arcpy.GetParameterAsText(0)
	trackid = arcpy.GetParameterAsText(1)
	outTable = arcpy.GetParameterAsText(2)

	rows, row = None, None

	try:
		rows = arcpy.InsertCursor(outTable)

		recComplete = 0

		# walk through each enemy sighting, create and insert a record into the table for each
		for datetimesighted, strength, activityattitude, weaponsequipment, \
		 disposition, intention, additionalobservations \
		 in enemysightingstodict(xmlfile):
			row = rows.newRow()
			row.SightingDateTime = parse_timestamp(datetimesighted)[0]
			row.Strength = strength
			row.ActivityAttitude = activityattitude
			row.WeaponsEquipment = weaponsequipment
			row.Disposition = disposition
			row.Intention = intention
			row.AdditionalObservations = additionalobservations
			''' Add the Track ID, which was passed as a parameter, to link report to a track '''
			row.FK_TrackGUID = trackid

			rows.insertRow(row)
			recComplete += 1

		arcpy.AddMessage("Processed " + str(recComplete) + " records.")

		arcpy.SetParameterAsText(3, 'True')

	except Exception as err:
		import traceback
		# Get the traceback object
		tb = sys.exc_info()[2]
		tbinfo = traceback.format_tb(tb)[0]

		# Concatenate information together concerning the error into a message string
		pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
		msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

		# Return python error messages for use in script tool or Python Window
		arcpy.AddError(pymsg)
		arcpy.AddError(msgs)

		# return a system error code
		sys.exit(-1)

	finally:
		if rows:
			del rows
		if row:
			del row

