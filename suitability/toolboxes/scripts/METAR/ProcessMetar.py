#####################################################################
# ProcessMetar.py - NOAA Metar Observed Weather                     #
#            Aggregated Live Feed processor                         #
#                                                                   #
# Created by: Paul Dodd - esri, Technical Marketing                 #
#                                                                   #
#      Build: 1.0.2, Apr 2012, P.D.                                 #
#         - Restructured code to better adhere to Python standards  #
#           and best practices.                                     #
#      Build: 1.0.1, Apr 2012, P.D.                                 #
#          - 'os.path.realpath' only supports 'strings', not None   #
#          - altered 'globals()['__file__'].split( os.sep)[1]' to   #
#            use 'os.path.split' instead                            #
#          - altered 'ConfigFileLoader().getValue' function to test #
#            for empty value, returning default                     #
#      Build: 1.0.0, Mar 2012                                       #
#	   Adapted Jun 2012 by David Martin for the MAoW Template		#
#                                                                   #
# Depends on: MetarDecoder.py - v1.0.1+, ALFlib.py - v1.0+          #
#####################################################################

#########################
# Import base libraries #
#########################

import time, shutil, sys, os

# Setup initial variables

home, scriptName = os.path.split( __file__)

###############################
# Load config file if present #
###############################

configFilename = scriptName.split( '.')[0] + '.cfg'

class ConfigFileLoader( object):
	# Class provides code issolation for configFile contents
	
	def logMessage( self, message):
		# Call 'self.logMessage' from ConfigFile to Log a message in Archive Log
		ALFlog.archive( message)
	
	if not os.access( configFilename, os.R_OK):
		sys.exit( " * Error * Unable to access configFile '{0}'!".format( configFilename))
	
	# Load file
	try:
		# Content loaded will be local to this Class
		execfile( configFilename)	# configFilename MUST be defined before load process,
		#                               or class user-defined methods will NOT be accessible!
	
	except Exception as e:
		sys.exit( " * Error * Failure during configFile load: {0}".format(e))

ConfigFile = ConfigFileLoader()

# Assign variables

filegdbName = getattr( ConfigFile, 'fileGDB', 'Metar')
if not filegdbName.endswith( '.gdb'):
	filegdbName += '.gdb'

featureclassName = getattr( ConfigFile, 'featureClass', 'CurrentMetar')
nickName = getattr( ConfigFile, 'nickName', 'CurrentMetar')
logRetention = getattr( ConfigFile, 'logRetention', 3)
logPath = os.path.realpath( getattr( ConfigFile, 'logPath', 'Logs'))
workPath = os.path.realpath( getattr( ConfigFile, 'workPath', 'Work'))
importPath = os.path.realpath( getattr( ConfigFile, 'importPath', ''))
outputSR = getattr( ConfigFile, 'outputCoordSys', 102100)	# WGS 1984 Web Mercator Auxiliary Sphere
outputTR = getattr( ConfigFile, 'outputTransformation', '')
spatialIndexGrid = getattr( ConfigFile, 'outputSpatialIndexGrid', [ 2500000, 0, 0])	# In units of output CoordSys
addRegistration = getattr( ConfigFile, 'addRegistration', True)
updateCurrent = getattr( ConfigFile, 'updateUsingCurrentCycle', False)

###########################
# Import custom libraries #
###########################

if importPath:
	# Add path to import
	sys.path.append( importPath)

from ALFlib import Logger
from MetarDecoder import MetarReader

ALFlog = Logger( nickName, logPath, logRetention)

# Make sure Work area is available
if workPath and not os.access( workPath, os.F_OK):
	try:
		os.makedirs( workPath)
	
	except Exception as e:
		sys.exit( " * Failed to create workPath '{0}': {1}".format( workPath, e))

sourceSR = 4326	# WGS 1984
errLimit = 0.10	# Error percent limit

# Extent Boundary (MinX, MinY, MaxX, MaxY), in Source Spatial Reference coordinates
layerExtent = [-179.9999, -80.0, 179.9999, 85.0]

# Import ArcPy library, retry if failure to initialize
importTrys = 3
importWait = 5

print "\nImporting ArcPy..."
while importTrys:
	try:
		import arcpy
		# Set Script arguments
		arcpy.gp.logHistory = False		# Turn off GP function logging
		arcpy.env.overwriteOutput = True	# Allow GP commands to overwrite GDB content
		
		if outputTR:
			# Set Tranformation
			arcpy.env.geographicTransformations = outputTR
		break
	
	except Exception as e:
		importTrys -= 1
		print "* Failed to import 'arcpy' library: {0}".format( e)
		if importTrys:
			print "Waiting {0} seconds...".format( importWait)
			time.sleep( importWait)
			print "Retrying..."

if not importTrys:
	sys.exit(1)

#######################################################
# Setup output Column details, maintaining column order

columns = []

def addCol( colRef, details):
	# Insert Column name in ordered list and add details to global Dict
	columns.append( colRef)
	globals()[ colRef] = details

# Change Order of or most details for any column below without needing to alter any other code!
addCol( 'colICAO',		{ 'Name': 'ICAO', 'Type': 'TEXT', 'Precision': None, 'Scale': None, 'Width': 4, 'Alias':None, 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colStationName',	{ 'Name': 'StationName', 'Type': 'TEXT', 'Precision': None, 'Scale': None, 'Width': 16, 'Alias':None, 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colCountry',		{ 'Name': 'Country', 'Type': 'TEXT', 'Precision': None, 'Scale': None, 'Width': 75, 'Alias':None, 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colUTC_DateTime',	{ 'Name': 'UTC_DateTime', 'Type': 'DATE', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':None, 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colLatitude',		{ 'Name': 'Latitude', 'Type': 'FLOAT', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':None, 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colLongitude',		{ 'Name': 'Longitude', 'Type': 'FLOAT', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':None, 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colElevation',		{ 'Name': 'Elevation_m', 'Type': 'FLOAT', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':'Elevation (m above sea level)', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colTemperature',	{ 'Name': 'Temperature_degC', 'Type': 'FLOAT', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':'Temperature (deg C)', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colDewPoint',		{ 'Name': 'DewPoint_degC', 'Type': 'FLOAT', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':'Dew Point (deg C)', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colHeatIndex',		{ 'Name': 'HeatIndex_degC', 'Type': 'FLOAT', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':'Heat Index (deg C)', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colRelativeHumidity',{ 'Name': 'RelativeHumidity_pc', 'Type': 'LONG', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':'Relative Humidity (%)', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colPressure',		{ 'Name': 'Pressure_mB', 'Type': 'FLOAT', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':'Pressure (mB at sea level)', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colWindChill',		{ 'Name': 'WindChill_degC', 'Type': 'FLOAT', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':'Wind Chill (deg C)', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colWindDirection',	{ 'Name': 'WindDirection_deg', 'Type': 'LONG', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':'Wind Direction (degrees)', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colWindGust',		{ 'Name': 'WindGust_kmph', 'Type': 'LONG', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':'Wind Gust (km/hr)', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colWindSpeed',		{ 'Name': 'WindSpeed_kmph', 'Type': 'LONG', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':'Wind Speed (km/hr)', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colVisibility',	{ 'Name': 'Visibility_km', 'Type': 'FLOAT', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':'Visibility (km)', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colCloudCover',	{ 'Name': 'CloudCover_pc', 'Type': 'LONG', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':'Cloud Cover (%)', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colCloudCeiling',	{ 'Name': 'CloudCeiling_ft', 'Type': 'LONG', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':'Cloud Ceiling (feet above ground)', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colPrecipitationRate',	{ 'Name': 'PrecipitationRate_cmph', 'Type': 'FLOAT', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':'Precipitation Rate (cm/hr)', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colSnowFall',	{ 'Name': 'SnowFall_yn', 'Type': 'SHORT', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':'Snow Fall (y/n)', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colSnowDepth',	{ 'Name': 'SnowDepth_cm', 'Type': 'FLOAT', 'Precision': None, 'Scale': None, 'Width': None, 'Alias':'Snow Depth (cm)', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colSkyCondition',	{ 'Name': 'SkyCondition', 'Type': 'TEXT', 'Precision': None, 'Scale': None, 'Width': 255, 'Alias':'Sky Condition', 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colWeather',		{ 'Name': 'Weather', 'Type': 'TEXT', 'Precision': None, 'Scale': None, 'Width': 125, 'Alias':None, 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})
addCol( 'colRemarks',		{ 'Name': 'Remarks', 'Type': 'TEXT', 'Precision': None, 'Scale': None, 'Width': 255, 'Alias':None, 'Nullable': 'NULLABLE', 'Required': 'NON_REQUIRED', 'Domain': None})

##########################################################
# Create Featureclass and open Insert and Update Cursors #
##########################################################

def openCursors( home, filegdbName, featureclassName, inputSR, outputSR, spatialGrid, update=False):
	workspace = os.path.join( home, filegdbName)
	featureclass = os.path.join( workspace, featureclassName)
	
	##########
	print "\nPreparing Workspace '{0}'...".format( filegdbName)
	if arcpy.Exists( workspace):
		if not update:
			try:
				# Delete Workspace
				shutil.rmtree( workspace)
			
			except Exception as e:
				print "  * Failed to remove existing FileGDB Workspace '{0}': {1}".format( workspace, e)
				sys.exit( 1)
	else:
		update = False
	
	if not update:
		try:
			# Create new Workspace
			arcpy.CreateFileGDB_management( home, filegdbName, 'CURRENT')
		
		except Exception as e:
			print "  * Failed to create FileGDB: {0}".format( e)
			sys.exit( 1)
	
	##########
	if update:
		update = arcpy.Exists( featureclass)
	
	if not update:
		print "  Creating Template Featureclass..."
		try:
			tempFC = arcpy.CreateFeatureclass_management( 'in_memory', featureclassName, 'POINT', None, None, None, outputSR, None, spatialGrid[0], spatialGrid[1], spatialGrid[2])
		
		except Exception as e:
			print "  * Failed to create Template Featureclass: {0}".format( e)
			sys.exit( 1)
		
		try:
			colNum = 0.0
			for colRef in columns:
				col = globals()[ colRef]
				colNum += 1
				sys.stdout.write( "\r    Adding fields...({0:3d}%)".format( int( colNum / len(columns) * 100)))
				arcpy.AddField_management( tempFC, col[ 'Name'], col['Type'], col['Precision'], col['Scale'], col['Width'], col['Alias'], col['Nullable'], col['Required'], col['Domain'])
		
		except Exception as e:
			print "\r    * Failure adding fields: {0}".format( e)
			sys.exit( 1)
		
		##########
		print "\r  Creating Output Featureclass '{0}' from Template...".format( featureclassName)
		try:
			arcpy.CreateFeatureclass_management( workspace, featureclassName, 'POINT', tempFC, None, None, outputSR, None, spatialGrid[0], spatialGrid[1], spatialGrid[2])
		
		except Exception as e:
			print "  * Failed to create Featureclass: {0}".format( e)
			sys.exit( 1)
		
		# Release objects
		del tempFC
		
		# Return Insert Cursor and None
		return arcpy.InsertCursor( featureclass, inputSR), None
	else:
		# Return Insert and Update Cursors
		return arcpy.InsertCursor( featureclass, inputSR), arcpy.UpdateCursor( featureclass, None, inputSR)

##################
# Set row values #
##################

def setRow( row, item):
	
	if 'ICAO' in item and item['ICAO']:
		row.setValue( colICAO['Name'], item['ICAO'][0: colICAO['Width']])
	else:
		row.setNull( colICAO['Name'])
	
	if 'Issuance' in item and item['Issuance']:
		row.setValue( colUTC_DateTime['Name'], item['Issuance'])
	else:
		row.setNull( colUTC_DateTime['Name'])
	
	if 'Name' in item and item['Name']:
		row.setValue( colStationName['Name'], item['Name'][0: colStationName['Width']])
	else:
		row.setNull( colStationName['Name'])
	
	if 'Country' in item and item['Country']:
		row.setValue( colCountry['Name'], item['Country'][0: colCountry['Width']])
	else:
		row.setNull( colCountry['Name'])
	
	if 'Latitude' in item and item['Latitude'] and 'Longitude' in item and item['Longitude']:
		row.setValue( colLatitude['Name'], item['Latitude'][0])
		row.setValue( colLongitude['Name'], item['Longitude'][0])
		row.setValue( 'Shape', arcpy.PointGeometry( arcpy.Point( item['Longitude'][0], item['Latitude'][0])))
	else:
		row.setNull( colLatitude['Name'])
		row.setNull( colLongitude['Name'])
		row.setNull( 'Shape')
	
	if 'Elevation' in item and item['Elevation']:
		row.setValue( colElevation['Name'], item['Elevation'][0])
	else:
		row.setNull( colElevation['Name'])
	
	if 'Temperature' in item and item['Temperature']:
		row.setValue( colTemperature['Name'], item['Temperature'][0])
	else:
		row.setNull( colTemperature['Name'])
	
	if 'DewPoint' in item and item['DewPoint']:
		row.setValue( colDewPoint['Name'], item['DewPoint'][0])
	else:
		row.setNull( colDewPoint['Name'])
	
	if 'RelHumidity' in item and item['RelHumidity']:
		row.setValue( colRelativeHumidity['Name'], item['RelHumidity'][0])
	else:
		row.setNull( colRelativeHumidity['Name'])
	
	if 'HeatIndex' in item and item['HeatIndex']:
		row.setValue( colHeatIndex['Name'], item['HeatIndex'][0])
	else:
		row.setNull( colHeatIndex['Name'])
	
	if 'Altimeter' in item and item['Altimeter']:
		row.setValue( colPressure['Name'], item['Altimeter'][0])
	else:
		row.setNull( colPressure['Name'])
	
	if 'Wind' in item:
		if 'Chill' in item['Wind'] and item['Wind']['Chill']:
			row.setValue( colWindChill['Name'], item['Wind']['Chill'][0])
		else:
			row.setNull( colWindChill['Name'])
		
		if 'Direction' in item['Wind'] and item['Wind']['Direction']:
			row.setValue( colWindDirection['Name'], item['Wind']['Direction'][0])
		else:
			row.setNull( colWindDirection['Name'])
		
		if 'Gust' in item['Wind'] and item['Wind']['Gust']:
			row.setValue( colWindGust['Name'], item['Wind']['Gust'][0])
		else:
			row.setNull( colWindGust['Name'])
		
		if 'Speed' in item['Wind'] and item['Wind']['Speed']:
			row.setValue( colWindSpeed['Name'], item['Wind']['Speed'][0])
		else:
			row.setNull( colWindSpeed['Name'])
	else:
		row.setNull( colWindChill['Name'])
		row.setNull( colWindDirection['Name'])
		row.setNull( colWindGust['Name'])
		row.setNull( colWindSpeed['Name'])
	
	if 'Visibility' in item and 'Prevailing' in item['Visibility'] and item['Visibility']['Prevailing']:
		row.setValue( colVisibility['Name'], item['Visibility']['Prevailing'])
	else:
		row.setNull( colVisibility['Name'])
	
	if 'CloudCoverage' in item and item['CloudCoverage']:
		sep = ''
		field = ''
		for val in item['CloudCoverage']:
			field += sep + val
			sep = ', '
		
		row.setValue( colSkyCondition['Name'], field[0: colSkyCondition['Width']])
	else:
		row.setNull( colSkyCondition['Name'])
	
	if 'PresentWeather' in item and item['PresentWeather']:
		sep = ''
		field = ''
		for val in item['PresentWeather']:
			field += sep + val
			sep = ', '
		
		row.setValue( colWeather['Name'], field[0: colWeather['Width']])
	else:
		row.setNull( colWeather['Name'])
	
	if 'Remarks' in item and item['Remarks']:
		sep = ''
		field = ''
		for val in item['Remarks']:
			if isinstance( val, str) and (val.find('Hourly Precipitation') != -1 or val.find('3-Hour Pressure') != -1):
				field += sep + val
				sep = ', '
		
		if field:		
			row.setValue( colRemarks['Name'], field[0: colRemarks['Width']])
	else:
		row.setNull( colRemarks['Name'])

	if 'TotalCloudCover' in item and item['TotalCloudCover']:
		row.setValue( colCloudCover['Name'], item['TotalCloudCover'])
	else:
		row.setNull( colCloudCover['Name'])

	if 'CloudCeiling' in item and item['CloudCeiling']:
		row.setValue( colCloudCeiling['Name'], item['CloudCeiling'])
	else:
		row.setNull( colCloudCeiling['Name'])

	if 'PrecipitationRate' in item and item['PrecipitationRate']:
		row.setValue( colPrecipitationRate['Name'], item['PrecipitationRate'])
	else:
		row.setNull( colPrecipitationRate['Name'])

	if 'SnowFall' in item and item['SnowFall']:
		row.setValue( colSnowFall['Name'], item['SnowFall'])
	else:
		row.setNull( colSnowFall['Name'])

	if 'SnowDepth' in item and item['SnowDepth']:
		row.setValue( colSnowDepth['Name'], item['SnowDepth'])
	else:
		row.setNull( colSnowDepth['Name'])


###################################
# Add Boundary Features to output #
###################################

def addBoundary( cursor, extent):
	# Set Min extent
	newRow = cursor.newRow()
	newRow.setValue( 'Shape', arcpy.PointGeometry( arcpy.Point( extent[0], extent[1])))
	cursor.insertRow( newRow)
	
	# Set Max extent
	newRow = cursor.newRow()
	newRow.setValue( 'Shape', arcpy.PointGeometry( arcpy.Point( extent[2], extent[3])))
	cursor.insertRow( newRow)
	
	# Release objects
	del newRow

##############
# Main logic #
##############

try:
	print "\nInitializing Metar Decoder..."
	Metar = MetarReader( False, False, updateCurrent)
	
	print "  Loading Weather Stations..."
	Metar.loadStations()
	
	print "  Processing observation data..."
	Metar.decode()
	
	print "  Observations - Read: {0}, Skipped: {1}, Unique Reports Found: {2}".format( Metar.totalObs, len(Metar.skipped), len(Metar))
	
except Exception as e:
	print "  * Failed to process Metar data: {0}".format( e)
	sys.exit( 1)

# Create Insert Feature Cursor (iFC) and Update Feature Cursor (uFC)
iFC, uFC = openCursors( workPath, filegdbName, featureclassName, sourceSR, outputSR, spatialIndexGrid, updateCurrent)

rowsOut = 0
rowsErr = 0
rowsReg = 0
rowCount = 0.0	# Create as Float
totalRows = len(Metar)
exitVal = 0
lastPercent = -1

if totalRows > 0:
	
	print
	row = None
	if uFC:
		# Update existing Rows if available
		for row in uFC:
			ICAO = row.getValue( colICAO['Name'])
			
			try:
				if ICAO in Metar:
					rowCount += 1
					
					progressPercent = int( rowCount / totalRows * 100)
					if progressPercent != lastPercent:
						# Only show update when % actually changes
						sys.stdout.write( "\rUpdating data..({0:3d}%)".format( progressPercent))
						lastPercent = progressPercent
				
					setRow( row, Metar[ ICAO])
					uFC.updateRow( row)
					Metar[ ICAO]['Processed'] = True
					
					rowsOut += 1
			
			except Exception as e:
				rowsErr += 1
				print "\r* Failed to update Observation for station '{0}':\n  '{1}'".format( ICAO, e)
				if (float(rowsErr) / totalRows) > errLimit:
					print "\n* Exceeded Error Limit percentage, giving up!"
					exitVal = 1
					break
	
	for item in Metar:
		# Insert Row if not already processed
		if not 'Processed' in item:
			rowCount += 1
			try:
				progressPercent = int( rowCount / totalRows * 100)
				if progressPercent != lastPercent:
					# Only show update when % actually changes
					sys.stdout.write( "\rWriting data...({0:3d}%)".format( progressPercent))
					lastPercent = progressPercent
				
				row = iFC.newRow()
				setRow( row, item)
				iFC.insertRow( row)
				
				rowsOut += 1
			
			except Exception as e:
				rowsErr += 1
				print "\r* Failed to write Observation for station '{0}':\n  '{1}'".format( item['ICAO'], e)
				if (float(rowsErr) / totalRows) > errLimit:
					print "\n* Exceeded Error Limit percentage, giving up!"
					exitVal = 1
					break

if not exitVal:
	print "\rWriting data...(Done)"
	
	if addRegistration and not uFC:
		# Add Extent Boundary features (Registration Marks)
		print "  Adding Extent Boundary..."
		addBoundary( iFC, layerExtent)
		rowsReg = 2	# account for registration features
		rowsOut += 2

ALFlog.archive( "Rows: (Unique) {0} - (Errors) {1} + (Registration) {2} = (Total Output) {3}".format( totalRows, rowsErr, rowsReg, rowsOut))

print "\nRows:        Unique:  {0: 5d}".format( totalRows)
print "             Errors: -{0: 5d}".format( rowsErr)
print "       Registration: +{0: 5d}".format( rowsReg)
print "       --------------------"
print "       Total Output: ={0: 5d}".format( rowsOut)

# Close and dispose of objects
try:
	del iFC
	del uFC
	del row
except:
	pass

# Invoke Deployment logic

if hasattr( ConfigFile, 'deploy') and callable( ConfigFile.deploy):
	print "\nRunning Deployment..."
	
	ConfigFile.deploy( os.path.join( workPath, filegdbName))

sys.exit( exitVal)
