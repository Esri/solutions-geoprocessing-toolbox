# Patrol Report (from XML) to Table
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
# add the 'PatrolReport' elements as a row to
# an ArcGIS Table of identical schema, against
# the specified Track ID
# INPUTS:
#	XML file (FILE)
#	Track ID (STRING)
# OUTPUTS:
#	Output Table (TABLE)
#-------------------------------------------------------------------------------

from xml.etree import ElementTree
from datetime import datetime
import arcpy, string
import re

def ptrlreptodict(xmlfile):
	''' Parses the xml to extract the PatrolReport fields into a dictionary '''

	PATROLREPORT_NS = '{http://helyx.co.uk/infopath/2003/myXSD/2010-06-09}'

	tree = ElementTree.parse(xmlfile)

	d = {}
	''' get each of the grouped nodes '''
	report = tree.find(PATROLREPORT_NS + 'Report')
	patrol = tree.find(PATROLREPORT_NS + 'Patrol')
	task = tree.find(PATROLREPORT_NS + 'Task')
	observations = tree.find(PATROLREPORT_NS + 'Observations')
	patrolcondition = tree.find(PATROLREPORT_NS + 'PatrolCondition')
	''' get report nodes '''
	reportnumber = report.find(PATROLREPORT_NS + 'ReportNumber').text
	classification = report.find(PATROLREPORT_NS + 'Classification').text
	_to = report.find(PATROLREPORT_NS + 'To').text
	_from = report.find(PATROLREPORT_NS + 'From').text
	reportdatetime = report.find(PATROLREPORT_NS + 'ReportDateTime').text
	''' get patrol nodes '''
	callsign = patrol.find(PATROLREPORT_NS + 'Callsign').text
	subunit = patrol.find(PATROLREPORT_NS + 'Subunit').text
	patrolbase = patrol.find(PATROLREPORT_NS + 'PatrolBase').text
	patroltype = patrol.find(PATROLREPORT_NS + 'PatrolType').text
	patrolcommand = patrol.find(PATROLREPORT_NS + 'PatrolCommand').text
	interpreter = patrol.find(PATROLREPORT_NS + 'Interpreter').text
	patrolsize = patrol.find(PATROLREPORT_NS + 'PatrolSize').text
	composition = patrol.find(PATROLREPORT_NS + 'Composition').text
	''' get task nodes '''
	opname = task.find(PATROLREPORT_NS + 'OpName').text
	taskname = task.find(PATROLREPORT_NS + 'TaskName').text
	taskdescription = task.find(PATROLREPORT_NS + 'TaskDescription').text
	''' get observation nodes '''
	terraindescription = observations.find(PATROLREPORT_NS + 'TerrainDescription').text
	miscinfo = observations.find(PATROLREPORT_NS + 'MiscInfo').text
	conclusions = observations.find(PATROLREPORT_NS + 'Conclusions').text
	''' ignore the EnemySightings nodes which go in another table '''
	''' get patrolcondition nodes '''
	numpatrolok = patrolcondition.find(PATROLREPORT_NS + 'NumPatrolOK').text
	numpatrolwounded = patrolcondition.find(PATROLREPORT_NS + 'NumPatrolWounded').text
	numpatrolkia = patrolcondition.find(PATROLREPORT_NS + 'NumPatrolKIA').text
	numpatrolmissing = patrolcondition.find(PATROLREPORT_NS + 'NumPatrolMissing').text
	numpatrolcaptured = patrolcondition.find(PATROLREPORT_NS + 'NumPatrolCaptured').text

	yield reportnumber, classification, _to, _from, reportdatetime, \
		  callsign, subunit, patrolbase, patroltype, patrolcommand, \
		  interpreter, patrolsize, composition, opname, taskname, \
		  taskdescription, terraindescription, miscinfo, conclusions, \
		  numpatrolok, numpatrolwounded, numpatrolkia, numpatrolmissing, \
		  numpatrolcaptured

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

		# walk through each patrol report, create and insert a record into the table for each
		for reportnumber, classification, _to, _from, reportdatetime, \
		 callsign, subunit, patrolbase, patroltype, patrolcommand, \
		 interpreter, patrolsize, composition, opname, taskname, \
		 taskdescription, terraindescription, miscinfo, conclusions, \
		 numpatrolok, numpatrolwounded, numpatrolkia, numpatrolmissing, \
		 numpatrolcaptured \
		 in ptrlreptodict(xmlfile):
			row = rows.newRow()
			row.ReportNumber = reportnumber
			row.Classification = classification
			row.ReportTo = _to
			row.ReportFrom = _from
			row.ReportDateTime = parse_timestamp(reportdatetime)[0]
			row.Callsign = callsign
			row.Subunit = subunit
			row.PatrolBase = patrolbase
			row.PatrolType = patroltype
			row.PatrolCommand = patrolcommand
			row.Interpreter = interpreter
			row.PatrolSize = patrolsize
			row.Composition = composition
			row.OpName = opname
			row.TaskName = taskname
			row.TaskDescription = taskdescription
			row.TerrainDescription = terraindescription
			row.MiscInfo = miscinfo
			row.Conclusions = conclusions
			row.NumPatrolOK = numpatrolok
			row.NumPatrolWounded = numpatrolwounded
			row.NumPatrolKIA = numpatrolkia
			row.NumPatrolMissing = numpatrolmissing
			row.NumPatrolCaptured = numpatrolcaptured
			''' Add the Track ID, which was passed as a parameter, to link report to a track '''
			row.FK_TrackGUID = trackid

			rows.insertRow(row)
			recComplete += 1

		arcpy.AddMessage("Processed " + str(recComplete) + " records.")

		arcpy.SetParameterAsText(3,'True')

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

