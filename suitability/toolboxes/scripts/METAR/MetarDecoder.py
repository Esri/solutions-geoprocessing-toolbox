#####################################################
# MetarDecoder.py - Metar observed weather decoder  #
#                                                   #
# Created by: Paul Dodd - esri, Technical Marketing #
#      Build: v1.0.2, Apr 2012, P.D.                #
#         - Restructured code to better adhere to   #
#           Python standards and best practices.    #
#         - Updated Observation cycle to read Last  #
#           and Current cycles when set to True.    #
#      Build: v1.0.1, Apr 2012, P.D.                #
#      Build: v1.0.0, Mar 2012                      #
#	   Amended Jun 2012 by David Martin             #
#                                                   #
# Depends on: ALFlib.py - v1.0+                     #
#####################################################

import ALFlib, os, sys, tempfile, time, urllib2
from datetime import datetime
from datetime import timedelta

class MetarReader( object):
	
	# Usage Help text

	"""Class: MetarReader( <verbose>, <decode>, <cycle>)
    Initialize new <object> to load and decode Metar Weather data,
    ordering items by ICAO station ID.

        Where:
            <verbose> is Boolean 'feedback' flag:
                (default) False = Do not provide any feedback.
                           True = Report progress feeback.

            <decode> is Boolean 'begin decode process' flag:
                         False = Do not initiate download and decoding process
                                 automatically.
                (default) True = Once intialization process is complete, auto-
                                 matically start download and decoding process.

            <cycle> is Boolean 'observation cycle' flag:
                (default) False = Read last Full-cycle of complete data.
                           True = Read last Full and Current cycle being updated.
                                  More current and complete!

    Decoded items are stored and accessed as a Dictionary having the form:

        {'%ObsDecoded': {'Standard': <#>, 'Remarks': <#>, 'Overall': <#>},
         'ICAO': '<stationID>', 'Name': '<stationName>', 'Country': '<str>',
         'Latitude': [<#>, '<units>'], 'Longitude': [<#>, '<units>'],
         'Elevation': [<#>, '<units>'], 'Issuance': <datetime_Object>,
         'ObsType': '<str>', 'Equipment': '<str>',
         'Wind': {'Direction': [<#>, '<units>'], 'Speed': [<#>, '<units>'],
                  'Gust': [<#>, '<units>'], 'Chill': [<#>, '<units>']},
         'Visibility': {'Min': '<str>', 'Prevailing': '<str>',
                        'Direction': '<str>'},
         'RVR': [{'Runway': '<str>', 'Min': '<str>', 'Max': '<str>',
                  'Tendency': '<str>'{1}, ...], 'PresentWeather': ['<str>', ...],
         'RecentWeather': ['<str>', ...], 'ForecastWeather': ['<str>', ...],
         'CloudCoverage': ['<str>', ...], 'TotalCloudCover': <#>,
		 'CloudCeiling': <#>, 'PrecipitationRate': <#>,	'SnowFall': <#>,
		 'SnowDepth': <#>, 'Temperature': [<#>, '<units>'],
         'DewPoint': [<#>, '<units>'], 'RelHumidity': [<#>, '<units>'],
         'HeatIndex': [<#>, '<units>'], 'Altimeter': [<#>, '<units>'],
         'SeaLevelPressure': [<#>, '<units>'], 'Remarks': ['<str>', ...],
         'METAR': '<str>'}

    Methods:
        '<object>.decode()' Initiate data download and decode process. Read
                            appropriate hourly observation cycle file from:
                    http://weather.noaa.gov/pub/data/observations/metar/cycles/
                    Details see: http://weather.noaa.gov/weather/metar.shtml.

    Properties:
             '<object>.verbose' Get or Set Boolean feedback flag.
             '<object>.skipped' Get String List of skipped data items.
                                (Includes reason skipped and raw Metar data)
        '<object>.currentCycle' Get or Set Boolean Observation cycle flag.

    Data lookup:
        '<object>[ <index>]' Where <index> = 0 to 'len( <object>)' - 1
        '<object>[ <str>]' Where <str> = ICAO station id.

    Use: 'if <str> in <object>' to query existance of a specific item.
         'for item in <object>' to iterate through indexed content.
         'len( <object>)' to query for total number of items.
"""
	
	version = "v1.0.2, March 2012, Paul Dodd - esri"
	
	# Add Report Observation Type
	obsType = {
		'AUTO': 'Fully Automated',
		'COR': 'Corrected',
		'RTD': 'Delayed'
	}
	
	# Add Equipment description
	equipment = {
		'AO1': 'Automatic w/o Rain-Snow Discriminator',
		'AO1A': 'Automatic w/o Rain-Snow Discriminator, augmented by Human',
		'AO2': 'Automatic w/Rain-Snow Discriminator',
		'AO2A': 'Automatic w/Rain-Snow Discriminator, augmented by Human'
	}
	# Add true-north direction for degree lookup x-ref
	direction = ALFlib.Constants.TrueNorth
	
	# Add tendency, support for Runway Visual Range
	tendency = {
		'U': 'Up',
		'D': 'Down',
		'N': 'No Change'
	}
	# Add Pressure Tendency, for Automatic Maintenance decoding
	pressureTendency = {
		'0': 'Increasing',
		'1': 'Increasing Slowly',
		'2': 'Increasing Steadily',
		'3': 'Increasing Rapidly',
		'4': 'Steady',
		'5': 'Decreasing',
		'6': 'Decreasing Slowly',
		'7': 'Decreasing Steadily',
		'8': 'Decreasing Rapidly'
	}
	# Add qualifier, support for Runway Visual Range
	qualifier = {
		'M': '<',
		'P': '>'
	}
	# Add Table of Weather and Obscuration for Significant Present, Forecast, and Recent Weather
	intensity = {	# 1, Phenomenon qualifier
		'-': 'Light',
		'': 'Moderate',
		'+': 'Heavy'
	}
	proximity = {	# 2, Phenomenon qualifier
		'VC': 'In Vicinity',
		'': 'On Station'
	}
	descriptor = {	# 3, Phenomenon qualifier
		'MI': 'Shallow',
		'BL': 'Blowing',
		'BC': 'Patchy',
		'SH': 'Showers',
		'PR': 'Partial',
		'DR': 'Low Drifting',
		'TS': 'Thunderstorms',
		'FZ': 'Freezing'
	}
	conjunction = {
		'TSDZ': 'with',
		'TSRA': 'with',
		'TSSN': 'with',
		'TSPL': 'with',
		'TSGS': 'with',
		'TSGR': 'with',
		'SHRA': 'of',
		'SHPL': 'of',
		'SHGS': 'of',
		'SHGR': 'of',
		'SHSN': 'of'
	}
	precipitation = {	# 4, Phenomenon type
		'DZ': 'Drizzle',
		'IC': 'Ice Crystals',
		'RA': 'Rain',
		'PL': 'Ice Pellets',
		'SN': 'Snow',
		'GR': 'Hail',
		'SG': 'Snow Grains',
		'GS': 'Small Hail and/or Snow Pellets',
		'UP': 'Unknown precipitation in automated observations'
	}
	obscuration = {	# 5, Phenomenon type
		'BR': 'Mist',
		'SA': 'Sand',
		'FG': 'Fog',
		'HZ': 'Haze',
		'FU': 'Smoke',
		'PY': 'Spray',
		'VA': 'Volcanic Ash',
		'DU': 'Widespread dust'
	}
	other = {	# 6, Phenomenon type
		'SQ': 'Squall',
		'FC': 'Funnel clouds',
		'+FC': 'Tornado or Waterspout',
		'SS': 'Sand Storm',
		'DS': 'Dust Storm',
		'PO': 'Well Developed Dust/Sand Whirls'
	}
	# Add Cloud detail
	coverage = {
		'NSC': 'No Significant Clouds',
		'NCD': 'No Clouds Detected',
		'CLR': 'Clear below 3700m',
		'SKC': 'Clear',
		'FEW': 'Few{0}',
		'SCT': 'Scattered{0}',
		'BKN': 'Broken{0}',
		'OVC': 'Overcast',
		'VV': 'Vertical Visibility'
	}
	# Add Cloud detail as percentage
	totalCloudCover = {
		'NSC': 0,
		'NCD': 0,
		'CLR': 0,
		'SKC': 0,
		'FEW': 20,
		'SCT': 45,
		'BKN': 75,
		'OVC': 100
	}
	# Add Airfield Visibility Color Codes
	visibilityCode = {
		'BLU': { 'Lowest': '2500ft', 'Min': '8000m'},
		'WHT': { 'Lowest': '1500ft', 'Min': '5000m'},
		'GRN': { 'Lowest': '700ft', 'Min': '3700m'},
		'YLO': { 'Lowest': '300ft', 'Min': '1600m'},
		'AMB': { 'Lowest': '200ft', 'Min': '800m'},
		'RED': { 'Lowest': '<200ft', 'Min': '<800m'},
		'BLACK': { 'Lowest': 'Unusable', 'Min': 'Unusable'},
	}
	# Add Remarks
	remarks = {
		'$': 'System requires maintenance',
		'ACC': 'Altocumulus Castellanus clouds',
		'ACSL': 'Altocumulus Standing Lenticular clouds',
		'ALQDS': 'All Quadrants',
		'AND': 'and',
		'ASOCTD': 'Associated',
		'AT': 'At',
		'BECMG': 'Becoming',
		'BIRD': 'Bird',
		'CB': 'Cumulonimbus clouds',
		'CBMAM': 'Cumulonimbus Mammatus clouds',
		'CCSL': 'Cirrocumulus Standing Lenticular clouds',
		'CHINO_LOC': 'Secondary Ceiling Sensor NOT operational',
		'CLDS': 'Clouds',
		'CONS': 'Continuous',
		'CU': 'Cumulus clouds',
		'DSNT': 'Distant',
		'E': 'to the East',
		'FM': 'From',
		'FROPA': 'due to Frontal Passage',
		'FRQ': 'Frequent',
		'FZRANO': 'Freezing Rain Sensor NOT operational',
		'HAZARD': 'Hazard',
		'IR': 'Ice on Runway',
		'LSR': 'Loose Snow on Runway',
		'LTG': 'Lightning',
		'LTGCA': 'Lightning, Cloud to Air',
		'LTGCC': 'Lightning, Cloud to Cloud',
		'LTGCG': 'Lightning, Cloud to Ground',
		'LTGIC': 'Lightning, In-Cloud',
		'LWR': 'Lower',
		'MOV': 'Moving',
		'MT': 'Mountains',
		'MTNS': 'Mountains',
		'N': 'to the North',
		'NE': 'to the North-East',
		'NOSIG': 'No Significant Changes Expected',
		'NSW': 'No Significant Weather',
		'NW': 'to the North-West',
		'OCNL': 'Occassional',
		'OHD': 'Overhead',
		'OVR': 'Over',
		'PNO': 'Tipping Rain Gauge NOT operational',
		'PRESRR': 'Pressure Rising Rapidly',
		'PRESFR': 'Pressure Falling Rapidly',
		'PSR': 'Packed Snow on Runway',
		'PWINO': 'Present Weather Identifier NOT operational',
		'RCR01': 'Runway Condition: 1',
		'RCR02': 'Runway Condition: 2',
		'RCR03': 'Runway Condition: 3',
		'RCR04': 'Runway Condition: 4',
		'RCR05': 'Runway Condition: 5',
		'RCR06': 'Runway Condition: 6',
		'RCR07': 'Runway Condition: 7',
		'RCR08': 'Runway Condition: 8',
		'RCR09': 'Runway Condition: 9',
		'RCR10': 'Runway Condition: 10',
		'RCR11': 'Runway Condition: 11',
		'RCR12': 'Runway Condition: 12',
		'RCR13': 'Runway Condition: 13',
		'RCR14': 'Runway Condition: 14',
		'RCR15': 'Runway Condition: 15',
		'RCR16': 'Runway Condition: 16',
		'RCR17': 'Runway Condition: 17',
		'RCR18': 'Runway Condition: 18',
		'RCR19': 'Runway Condition: 19',
		'RCR20': 'Runway Condition: 20',
		'RCR21': 'Runway Condition: 21',
		'RCR22': 'Runway Condition: 22',
		'RCR23': 'Runway Condition: 23',
		'RCR24': 'Runway Condition: 24',
		'RCR25': 'Runway Condition: 25',
		'RCRNR': 'Runway Condition: No Report',
		'RVRNO': 'RVR-but no report',
		'RWY': 'Runway',
		'S': 'to the South',
		'SCSL': 'Stratocumulus Standing Lenticular clouds',
		'SE': 'to the South-East',
		'SFC': 'Surface',
		'SW': 'to the South-West',
		'TCU': 'Towering Cumulus clouds',
		'TEMPO': 'Temporary',
		'TL': 'Till',
		'TSNO': 'Lightning Detection Sensor NOT operational',
		'VIRGA': 'Virga',
		'VIS': 'Visible',
		'VISNO_LOC': 'Secondary Visibility Sensor NOT operational',
		'VRB': 'Variable',
		'W': 'to the West',
		'WR': 'Wet Runway'
	}
	
	# Observations successfully decoded and ready for use
	obs = {}
	# List of Observations above ordered by ICAO id
	orderedObs = []
	# Raw data skipped, each element contains a row of data w/reason it was skipped
	skipped = []
	
	weatherStations = None
	timeStamp = None
	
	# Raw data split into Items needing decoding
	data = []
	
	# Data Item that couldn't be decoded, plus counts for Standard and Remark locations found
	undecoded = {}
	
	verbose = False
	
	totalObs = 0	# Total observations read
	hundred = 0		# Total observations w/100% of their Standatd Items decoded
	notHundred = 0	# Total observations w/less than 100% of their Standatd Items decoded
	
	###################
	# Class Initializer
	def __init__( self, verbose=False, decode=True, cycle=False):
		self.verbose = verbose
		self.currentCycle = cycle
		if decode:
			self.decode()
	
	#######################################
	# Report if item is in Dictionary cache
	def __contains__( self, item):
		return (item in self.obs)
	
	###################################################
	# Return item or indexed item from Dictionary cache
	def __getitem__( self, item):
		if isinstance( item, int) or isinstance( item, long):
			if item < 0 or item >= len( self.obs):
				raise IndexError( item)
			else:
				return self.obs[ self.orderedObs[ item]]
		
		if not item in self.obs:
			raise KeyError( item)
		else:
			return self.obs[ item]
	
	######################################
	# Return number of items in Dictionary
	def __len__( self):
		return len( self.obs)
	
	################################
	# Load Weather Station details #
	################################
	
	def loadStations( self):
		if self.verbose:
			sys.stdout.write( "\nLoading Weather Stations...")
		
		self.weatherStations = ALFlib.WeatherStationLoader( 1) # Load using ICAO station ids
		
		if self.verbose:
			sys.stdout.write( "Done\n")
	
	##############################
	# Read and Decode Metar data #
	##############################
	
	def decode( self, argv=[]):
		argc = len(argv)
		
		if not self.weatherStations:
			self.loadStations()
		
		utcNow = datetime.utcnow()
		hour = utcNow.hour

		cycles = []

		if utcNow.minute < 50:
			# Grab last complete cycle
			hour -= 1
			if hour < 0:
				hour = 23

		cycles.append( hour)	# Include last complete cycle

		if self.currentCycle:
			hour = utcNow.hour

			if utcNow.minute >= 50:
				# Grab next cycle, else use this cycle
				hour += 1
				if hour > 23:
					hour = 0
			
			cycles.append( hour)	# Add current partial cycle
		
		if self.verbose:
			print utcNow + timedelta(1)
		
		if self.verbose:
			print "Accessing Metar URL..."

		self.totalObs = 0
		self.hundred = 0
		self.notHundred = 0
		
		# Clear current data
		if self.obs:
			self.obs = {}
			self.orderedObs = []
			self.skipped = []
		
		# Process each cycle
		for hour in cycles:		
			fileName = "{0:02d}Z.TXT".format( hour)
			source = "http://weather.noaa.gov/pub/data/observations/metar/cycles/{0}".format( fileName)
			
			iFP = urllib2.urlopen( source)
			
			if self.verbose:
				print "\nReading: {0}, {1}:{2}".format( fileName, utcNow.hour, utcNow.minute)
			
			line = True
			
			while line:
				line = iFP.readline()
				
				try:
					if len(line) > 15:
						if (line[4] == "/") and (line[7] == "/") and (line[13] == ":"):
							# Date/Time stamp
							self.timeStamp = datetime( int(line[0:4]), int(line[5:7]), int(line[8:10]), int(line[11:13]), int(line[14:16]))
						else:
							# Observation record
							self.totalObs += 1
							
							self.data = line.split()
							
							ok2print = False
							for index in range(0, argc):
								if line.find( argv[index]) != -1:
									if (index + 1) == argc:
										ok2print = True
								else:
									break
							
							observation = self.decodeMetar()
							
							if type( observation) == dict and 'ICAO' in observation:
								observation[ 'METAR'] = line
								
								# Add item to Ordered list
								if observation[ 'ICAO'] not in self.obs:
									self.orderedObs.append( observation[ 'ICAO'])
								
								# Add/Update item in Dictionary
								self.obs[ observation[ 'ICAO']] = observation
								
								if observation[ '%ObsDecoded'][ 'Standard'] != 100:
									self.notHundred += 1
								else:
									self.hundred += 1
								for index in range(0, argc):
									if observation[ 'ICAO'] == argv[index]:
										ok2print = True
							else:
								observation = "* {0} *\n{1}".format( observation, line)
								self.skipped.append( observation)
							
							if ok2print:
								print
								if type( observation) == dict and 'METAR' in observation:
									print "* Raw METAR data:\n{0}".format( observation[ 'METAR'])
									print "* Decoded values:"
								print observation
				
				except Exception as e:
					sys.stderr.write( "\n* Error processing data line: {0}  Err: '{1}'\n".format( line, e))
					self.skipped.append( "* Error processing line *\n{0}".format( line))
			
			iFP.close()
		
		# Sort ordered List
		self.orderedObs.sort()
		
		# Print undecoded items amd counts, found in 'Standard' or 'Remark' sections
		# (selected by argument keyword)
		if argc == 1:
			if argv[0] == 'Skipped':
				for item in self.skipped:
					print item
			
			for (key, value) in self.undecoded.iteritems():
				if argv[0] in value and value[ argv[0]] > 0:
					print "'{0}': {1}".format( key, value)
		
		if self.verbose:
			percent = int( self.hundred / float(self.hundred + self.notHundred) * 100)
			unique = 0
			for item in self.obs.itervalues():
				if item['%ObsDecoded']['Standard'] == 100:
					unique += 1
			uniquePercent = int( unique / float(len(self.obs)) * 100)
			
			print "\nObservations - Read: {0}, Skipped: {1}, Unique: {2}".format( self.totalObs, len( self.skipped), len( self.obs))
			print "    w/100% Standard items Decoded:{0: 6d} ({1:2d}%), Unique:{2: 5d} ({3:2d}%)".format( self.hundred, percent, unique, uniquePercent)
			print "                        Ramaining:{0: 6d} ({1:2d}%)".format( self.notHundred, 100 - percent)
	
	#############################
	# Decode Metar station data #
	#############################
	
	# Get next item (text/word seperated by whitespace) in data string, incrementing index and return 'value'
	def getNext( self, success=True):
		self.valueIndex += 1
		
		if success:
			self.decoded += 1	# Total decoded
			if self.foundRemark:
				self.remarksDecoded += 1
			else:
				self.standardDecoded += 1
		else:
			idx = self.valueIndex - 1
			if idx >= 0 and idx < len(self.data):
				if not self.data[ idx] in self.undecoded:
					self.undecoded[ self.data[ idx]] = {
						'Standard': 0,
						'Remark': 0
					}
				
				if self.foundRemark:
					self.undecoded[ self.data[ idx]][ 'Remark'] += 1
				else:
					self.undecoded[ self.data[ idx]][ 'Standard'] += 1
		
		if self.valueIndex < len( self.data):
			value = self.data[ self.valueIndex]
			if (value == 'METAR') or (value == 'SPECI'):
				value = self.getNext()
				if (self.valueIndex > 1) and (value in self.weatherStations):
					# another Observation detected on same line
					self.valueIndex = len(self.data)
					return ''
			elif (len(value) >= 3) and (value[0:3] == 'RMK'):
				# Found start of Remarks
				self.foundRemark = True
				self.remarkIndex = self.valueIndex
				value = self.getNext()
			
			if value:
				try:
					return value.decode()
				
				except Exception as e:
					sys.stderr.write( "* Invalid Content: '{0}', ignored *\n".format( value))
					return self.getNext( False)
		
		return ''
	
	# Peek at next item without changing current details
	def peekNext( self):
		if (self.valueIndex + 1) < len( self.data):
			try:
				return self.data[ self.valueIndex + 1].decode()
			
			except:
				pass
		
		return ''
	
	# Decode record
	def decodeMetar( self):
		# Decode Metar data, return new row as Dict
		obs = {
			'%ObsDecoded': { 'Standard': 0, 'Remarks': 0, 'Overall': 0},
			'ICAO': '',
			'Name': '',
			'Latitude': [],
			'Longitude': [],
			'Elevation': [],
			'Country': '',
			'Issuance': '',
			'ObsType': '',
			'Equipment': '',
			'Wind': {
				#'Direction': []
				#'Speed': []
				#'Gust': []
				#'Chill': []
			},
			'Visibility': {
				#'Min': ''
				#'Prevailing': ''
				#'Direction': ''
			},
			'RVR': [],
			'PresentWeather': [],
			'RecentWeather': [],
			'ForecastWeather': [],
			'CloudCoverage': [],
			'TotalCloudCover': 0,
			'CloudCeiling': 0,
			'PrecipitationRate': 0,
			'SnowFall': 0,
			'SnowDepth': 0,
			'Temperature': [],
			'DewPoint': [],
			'RelHumidity': [],
			'HeatIndex': [],
			'Altimeter': [],
			'SeaLevelPressure': [],
			'Remarks': [],
			'METAR': ''
		}
		
		self.valueIndex = -1
		self.decoded = 0
		self.standardDecoded = 0
		self.remarksDecoded = 0
		self.remarkIndex = len( self.data)
		self.foundRemark = False	# Has Remark indicator been found?
		
		value = ""
		
		if self.data:
			value = self.getNext( False)	# Get initial but don't inc successful process count
			valLen = len(value)
			
			if value == 'TAF':
				return "METAR data expected not TAF"
			else:
				# Verify station ID
				if self.weatherStations and value not in self.weatherStations:
					return "Unlisted ICAO station"
				else:
					station = self.weatherStations[ value]
					# Verify required Station details
					if not ('Latitude' in station and isinstance( station[ 'Latitude'], float) and \
					        'Longitude' in station and isinstance( station[ 'Longitude'], float)):
						return "Missing ICAO station location (Lat/Long)"

					if station[ 'Latitude'] < -90 or station[ 'Latitude'] > 90 or \
					   station[ 'Longitude'] < -180 or station[ 'Longitude'] > 180:
						return "Invalid ICAO station location (Lat/Long)"
					
					# Pull Station details
					obs[ 'ICAO'] = value
					obs[ 'Name'] = station[ 'Name'].title()
					obs[ 'Latitude'] = [ station[ 'Latitude'], 'degrees']
					obs[ 'Longitude'] = [ station[ 'Longitude'], 'degrees']
					if station[ 'Elevation']:
						obs[ 'Elevation'] = [int( station[ 'Elevation'].strip('m')), 'meters']
					obs[ 'Issuance'] = self.timeStamp
					
					if station['Province']:
						obs[ 'Country'] = station['Country'].title() + ": " + station['Province'].title()
					else:
						obs[ 'Country'] = station['Country'].title()
					
					value = self.getNext()
					valLen = len(value)
					
					wholeVis = 0	# clear whole number holding, for S.M. visibility processing
					
					# Clear Decode Once flags
					visDecoded = False	# Has Visibility values been decoded yet?
					windDecoded = False	# Has Wind values been decoded yet?
					issuanceDecoded = False	# Has Issuance date/time been decoded yet?
					tempNdewDecoded = False	# Has Temp and Dew Point been decoded yet?
					altDecoded = False	# Has Altimeter value been decoded yet?
					forecastConditions = False	# Are Temporary Weather conditions in effect?
					
					# Parse values
					while value:
						getNext = True	# OK to get next item?
						success = False	# was processing of last item successful?
						
						#################
						# Process Remarks
						#
						if self.foundRemark:
							success = True	# Start as True
							
							#if value in self.remarks:
							#	obs[ 'Remarks'].append( self.remarks[ value])
							if valLen > 2 and value[0:2] == 'AO':
								# Refine Equipment used by Automated Observations
								if value in self.equipment:
									obs[ 'Equipment'] = self.equipment[ value]
								else:
									obs[ 'Equipment'] = value
							elif valLen > 3 and value[0:3] == 'SLP' and value[3:].isdigit():
								# Handle Sea Level Pressure reading
								obs[ 'SeaLevelPressure'] = [1000 + (float( value[3:]) / 10), 'millibars']
							elif value.count('-') == 1 and value.split( '-')[0] in self.remarks and  value.split( '-')[1] in self.remarks:
								# Disect '?-?' range
								values = value.split( '-')
								values[0] = self.remarks[ values[0]]
								values[1] = self.remarks[ values[1]]
								if values[0].rsplit( None, 1)[0] == values[1].rsplit( None, 1)[0]:
									# Both are directions 'to the' NSEW...
									val = "{0} through {1}".format( values[0].rsplit( None, 1)[1], values[1].rsplit( None, 1)[1])
								else:
									val = "{0} {1}".format( values[0], values[1])
								obs[ 'Remarks'].append( val)
							elif valLen == 5 and value[0] == 'P' and value[1:].isdigit():
								# Hourly Precipitation Amount, in hundredths of inches
								val = 25.4 * float(value[1:]) / 100
								obs[ 'PrecipitationRate'] = val/10 #cm/hr
								obs[ 'Remarks'].append( "Hourly Precipitation Amount: {0:0.01f}mm".format( val))
							elif valLen == 5 and value[0] == '1' and value.isdigit():
								# 6-Hour Max Temp
								obs[ 'Remarks'].append( "6-Hour Maximum Temperature: {0:0.01f}c".format( self.decodeAutoMaintTemp( value)))
							elif valLen == 5 and value[0] == '2' and value.isdigit():
								# 6-Hour Min Temp
								obs[ 'Remarks'].append( "6-Hour Minimum Temperature: {0:0.01f}c".format( self.decodeAutoMaintTemp( value)))
							elif valLen == 5 and value[0] == '3' and value.isdigit():
								# 3-Hour Precipitation Amount, in hundredths of inches
								val = 25.4 * float(value[1:]) / 100
								obs[ 'PrecipitationRate'] = val/30 #cm/hr
								obs[ 'Remarks'].append( "3-Hour Precipitation Amount: {0:0.01f}mm".format( val))
							elif valLen == 5 and value[0:2] == '4/' and value[ 2:].isdigit():
								# Snow-Depth on Ground, in inches
								val = 25.4 * float(value[2:])
								obs[ 'SnowDepth'] = val/10 #cm
								obs[ 'Remarks'].append( "Snow-Depth on Ground: {0:0.01f}mm".format( val))
							elif valLen == 9 and value[0] == '4' and value.isdigit():
								# 24-Hour Max and Min Temp
								for desc, val in ['Maximum', value[ 1:5]],['Minimum', value[ 5:]]:
									obs[ 'Remarks'].append( "24-Hour {0} Temperature: {1:0.1f}c".format( desc, self.decodeAutoMaintTemp( val)))
							elif valLen == 5 and value[0] == '5' and value.isdigit():
								# 3-Hour Pressure Tendency, in tenths of millibars
								if value[ 2:] == '000':
									val = ""
								else:
									val = ": {0:0.01f}mb".format( float(value[ 2:]) / 10)
								if value[1] in self.pressureTendency:
									val = " " + self.pressureTendency[ value[1]] + val
								obs[ 'Remarks'].append( "3-Hour Pressure{0}".format( val))
							elif valLen == 5 and value[0] == '6' and value.isdigit():
								# 6-Hour Precipitation Amount, in hundredths of inches
								val = 25.4 * float(value[1:]) / 100
								obs[ 'PrecipitationRate'] = val/60 #cm/hr
								obs[ 'Remarks'].append( "6-Hour Precipitation Amount: {0:0.01f}mm".format( val))
							elif valLen == 5 and value[0] == '7' and value.isdigit():
								# 24-Hour Precipitation Amount, in hundredths of inches
								val = 25.4 * float(value[1:]) / 100
								obs[ 'PrecipitationRate'] = val/240 #cm/hr
								obs[ 'Remarks'].append( "24-Hour Precipitation Amount: {0:0.01f}mm".format( val))
							elif valLen == 6 and value[0:3] == '933' and value.isdigit():
								# Water Equivalent of Snow on Ground, in tenths of inches
								val = 25.4 * float(value[2:]) / 10
								obs[ 'Remarks'].append( "Snow/Water on Ground: {0:0.01f}mm".format( val))
							elif valLen == 5 and value[0:2] == '98' and value.isdigit():
								# Duration of Sunshine, in minutes
								val = int(value[2:])
								obs[ 'Remarks'].append( "Minutes of Sunshine: {0}".format( val))
							elif valLen == 9 and value[0] == 'T' and value[1:].isdigit():
								# Hourly Temp and Dew Point in celsius
								for desc, val in ['Temperature', value[ 1:5]],['Dew Point', value[ 5:]]:
									obs[ 'Remarks'].append( "Hourly {0}: {1:0.1f}c".format( desc, self.decodeAutoMaintTemp( val)))
							elif value in self.visibilityCode:
								pass
							else:
								success = False
						
						#####################################
						# Process Standard Observation values
						#
						if not success:		# Not decoded by Remark Handler
							success = True	# Start as True
							
							# Check Issuance date/time
							if valLen >= 7 and value[ 0:6].isdigit() and value[6] == 'Z':
								if issuanceDecoded:
									success = False
								else:
									issuanceDecoded = True
									
									values = value.split( 'Z')
									
									day = int(values[0][0:2])	# Issuance Day
									month = self.timeStamp.month
									year = self.timeStamp.year
									
									if abs(day - self.timeStamp.day) > 20:
										# There is a shift from one Month to the next
										if self.timeStamp.day > day:
											# Issuance is for Next Month
											month += 1
											if month > 12:
												year += 1
												month = 1
										else:
											# Issuance is for Last Month
											month -= 1
											if month <= 0:
												year -= 1
												month = 12
									
									obs[ 'Issuance'] = datetime( year, month, day, int(values[0][2:4]), int(values[0][4:6]))
									
									# Handle additional values following 'Z', if any
									if len( values) > 1 and values[1]:
										value = values[1]
										valLen = len(value)
										getNext = False
							
							# Check for Observation, Automated Equipment or Corrected
							elif value in self.obsType:
								obs[ 'ObsType'] = self.obsType[ value]
							
							# Check for Wind conditions
							elif value.endswith( 'KT') or value.endswith( 'KTS') or value.endswith( 'MPS') or value.endswith( 'KMH'):
								if windDecoded and not (self.foundRemark or forecastConditions):
								#if windDecoded:
									success = False
								else:
									windDecoded = True
									
									if self.foundRemark:
										obs[ 'Remarks'].append( { 'Wind': self.decodeWindConditions( value)})
									elif forecastConditions:
										obs[ 'ForecastWeather'].append( {'Wind': self.decodeWindConditions( value)})
									else:
										obs[ 'Wind'] = self.decodeWindConditions( value)
							
							# Check for Visibility, number greater than a fraction for S.M.
							elif (valLen <= 2) and value.isdigit():
								if visDecoded and not (self.foundRemark or forecastConditions):
									success = False
								else:
									wholeVis = int(value)
							
							# Check for Visibility, U.S. in Statute Miles
							elif valLen > 2 and value.endswith( 'SM'):
								if visDecoded and not (self.foundRemark or forecastConditions):
									success = False
								else:
									visDecoded = True

									if value[0] in self.qualifier:
										val = self.qualifier[ value[0]]
										value = value[ 1:valLen]
										valLen = len(value)
									else:
										val = None

									#ignoring qualifier as visibility is now a float field
									val = None
									
									# Get visibility in Statute Miles and convert to Meters
									value = value[ 0:(valLen - 2)].split('/')
									valLen = len(value)
									if valLen > 1:
										if value[0].isdigit() and value[1].isdigit():
											val = ( wholeVis + (float(value[0]) / float(value[1]))) * 1.609
										wholeVis = 0	# clear whole number holding
									else:
										if value[0].isdigit():
											val = int(value[0]) * 1.609
									
									# Save if there is content to save
									if val:
										if self.foundRemark:
											obs[ 'Remarks'].append( { 'Visibility': { 'Prevailing': val}})
										elif forecastConditions:
											obs[ 'ForecastWeather'].append( { 'Visibility': { 'Prevailing': val}})
										else:
											obs[ 'Visibility']['Prevailing'] = val
							
							# (cont) Check for Prevailing Visibility and optional minimum w/direction, in Meters
							elif ((valLen == 4 and value.isdigit()) or 
								(valLen == 5 and value[0] in self.qualifier and value[1:].isdigit()) or 
								(valLen >= 7 and valLen <= 8 and value.endswith( 'NDV') and value[(valLen - 7):(valLen - 3)].isdigit())):
								if visDecoded and not (self.foundRemark or forecastConditions):
									success = False
								else:
									visDecoded = True
									
									val = {
									}
									
									# Remove 'Non-Directional Visibility' indicator
									value = value.replace('NDV', '')
									valLen = len(value)
									
									if value[0] in self.qualifier:
										val['Prevailing'] = self.qualifier[ value[0]]
										value = value[ 1:valLen]
										valLen = len(value)
									else:
										val['Prevailing'] = None

									#ignoring qualifier as visibility is now a float field
									val['Prevailing'] = None
									
									if value == '9999':
										val['Prevailing'] = "10" # >= 10km
									else:
										val['Prevailing'] = int(value)/1000
									
									# Check for lowest visibility and optional direction
									value = self.peekNext()
									valLen = len(value)
									if valLen >= 4 and value[ 0:4].isdigit():
										if valLen == 4:
											val['Min'] = "{0}m".format( int(value))
										else:
											if value[ 4:] and value[ 4:].strip( 'NSEW') == "":
												val['Min'] = "{0}m".format( int(value[ 0:4]))
												if value[ 4:] in self.direction:
													val['Direction'] = [self.direction[ value[ 4:]], 'degrees']
										
										self.getNext()	# Pop 'peeked' item from list
									
									if self.foundRemark:
										obs[ 'Remarks'].append( { 'Visibility': val})
									elif forecastConditions:
										obs[ 'ForecastWeather'].append( { 'Visibility': val})
									else:
										obs[ 'Visibility'] = val
							
							# (cont) Check for Visibility, other CAVOK
							elif value == 'CAVOK':
								if visDecoded and not (self.foundRemark or forecastConditions):
									success = False
								else:
									visDecoded = True
									
									val = "10" # >= 10km
									
									if self.foundRemark:
										obs[ 'Remarks'].append( { 'Visibility': { 'Prevailing': val}})
									elif forecastConditions:
										obs[ 'ForecastWeather'].append( { 'Visibility': { 'Prevailing': val}})
									else:
										obs[ 'Visibility']['Prevailing'] = val
							
							# Check for Runway Visual Range, multiple
							elif valLen >= 3 and (value[0] == 'R') and value[1:3].isdigit():
								Runway = {
									'Runway': ''
									#'Min': '',
									#'Max': '',
									#'Tendency': ''
								}
								for rvr in value.split("/"):
									if rvr:
										if rvr[0] == 'R' and len(rvr) > 2:
											if len(rvr) == 3:
												Runway[ 'Runway'] = "{0}".format( int( rvr[ 1:]))
											else:
												Runway[ 'Runway'] = "{0}{1}".format( int( rvr[ 1:3]), rvr[ 3:])
										elif rvr in self.tendency:
											Runway[ 'Tendency'] = self.tendency[ rvr]
										else:
											if rvr.find( 'FT') != -1:
												units = 0.3048 # ft
											else:
												units = 1 # km
											
											for var in rvr.split( 'V'):
												varOff = 0
												varLen = len(var)
												varVal = ''
												if var[0] in self.qualifier:
													varVal = self.qualifier[ var[0]]
													varOff += 1
												if var[ varLen - 1] in self.tendency:
													varLen -= 1
													Runway[ 'Tendency'] = self.tendency[ var[ varLen]]
												if var.find( 'FT') != -1:
													varLen -= 2
												if var[ varOff:varLen].isdigit():
													varVal += "{0}m".format( int( float( var[ varOff:varLen]) * units))
													if 'Max' not in Runway:
														Runway[ 'Max'] = varVal
													else:
														Runway[ 'Min'] = Runway[ 'Max']
														Runway[ 'Max'] = varVal
								
								obs[ 'RVR'].append( Runway)
							
							# Check for Cloud coverage, multiple
							elif (valLen >= 3 and value[ 0:3] in self.coverage) or (valLen == 5 and value[ 0:2] in self.coverage):
								val = self.decodeCloudCover( value)
								
								if val:
									if self.foundRemark:
										obs[ 'Remarks'].append( val)
									elif forecastConditions:
										obs[ 'ForecastWeather'].append( val)
									else:
										obs[ 'CloudCoverage'].append( val)
								else:
									success = False

								# Also check for Total Cloud Cover, replacing the current value held if this value is greater
								val = self.decodeTotalCloudCover( value)

								if obs[ 'TotalCloudCover']:
									if val > obs[ 'TotalCloudCover']:
										obs[ 'TotalCloudCover'] = val
								else:
									obs[ 'TotalCloudCover'] = val

								# And further check for Cloud Ceiling, which is the height of the lowest BKN or OVC layer
								val = self.decodeCloudCeiling( value)

								if obs[ 'CloudCeiling']:
									if val < obs[ 'CloudCeiling']:
										obs[ 'CloudCeiling'] = val
								else:
									obs[ 'CloudCeiling'] = val
							
							# Check for Temp and Dew point, then compute Relative Humidity and Heat Index
							elif (valLen >= 3 and valLen <= 7) and (value.count( '/') >= 1) and value.strip('M')[0:2].isdigit():
							#elif (valLen >= 5 and valLen <= 7) and (value.find( '/') != -1):
								if tempNdewDecoded:
									success = False
								else:
									tempNdewDecoded = True
									
									values = value.split( '/', 1)
									if values and values[0]:
										for val in values:
											if val.strip('M').isdigit():
												units = 1
												if val[0] == 'M':
													units = -1
												
												val = [int(val.strip('M')) * units, 'celsius']
												
												# Check if no Temp saved and input Temp is not null
												if not obs[ 'Temperature']:
													obs[ 'Temperature'] = val
												else:
													obs[ 'DewPoint'] = val 
										
										if obs[ 'Temperature']:
											if obs[ 'DewPoint']:
												# Compute Relative Humidity
												val = ALFlib.relativeHumidity( obs[ 'Temperature'][0], obs[ 'DewPoint'][0])
												if val:
													obs[ 'RelHumidity'] = [int( round( val)), 'percent']
													# Compute Heat Index
													val = ALFlib.heatIndex( obs[ 'Temperature'][0], val)
													if val:
														obs[ 'HeatIndex'] = [ round( val * 10) / 10, 'celsius']
											if 'Speed' in obs[ 'Wind'] and obs[ 'Wind'][ 'Speed'] and obs[ 'Wind'][ 'Speed'][0] > 0:
												# Compute Wind Chill
												val = ALFlib.windChill( obs[ 'Temperature'][0], obs[ 'Wind'][ 'Speed'][0])
												if val:
													obs[ 'Wind'][ 'Chill'] = [ round( val * 10) / 10, 'celsius']
										else:
											success = False
							
							# Check for Altimeter setting
							elif valLen == 5 and (value[0] == 'A' or value[0] == 'Q') and value[1:].isdigit():
								if not altDecoded:	# Ignore second+ reading
									altDecoded = True
									
									if value[0] == 'A':	# Pressure in Inches of Mercury, convert to millibars
										obs[ 'Altimeter'] = [round( float( value[1:]) / 2.9532, 1), 'millibars']
									else:	# 'Q', Pressure in Hectopascals or Millibars
										obs[ 'Altimeter'] = [float( value[1:]), 'millibars']
							
							# Check for No-Data '/' chars in data, skip if all char are '/'
							elif not value.replace( '/', ''):
								pass
							
							# Check for Airfield Color Codes, multiple
							elif valLen >=3 and value[0:3] in self.visibilityCode:
								pass
							
							# Check for No Significant Weather to report
							elif value == 'NSW':
								obs[ 'ForecastWeather'].append( self.remarks[ value])
							
							# Check for No Significant Changes Expected
							elif valLen >= 4 and value[ 0:4] == 'NOSI':
								obs[ 'ForecastWeather'].append( self.remarks[ 'NOSIG'])
							
							# Check for Forecast Weather change
							elif value == 'TEMPO' or value == 'BECMG':
								obs[ 'ForecastWeather'].append( self.remarks[ value])
								forecastConditions = True
							
							# Check for Forecast Weather change
							elif valLen == 6 and (value[ 0:2] == 'AT' or value[ 0:2] == 'FM' or value[ 0:2] == 'TL') and value[ 2:].isdigit():
								obs[ 'ForecastWeather'].append( "{0} {1}:{2}Z".format( self.remarks[ value[0:2]], value[2:4], value[4:]))
								forecastConditions = True
							
							# Check for Present/Recent Weather details, multiple
							else:
								if valLen > 2 and value[ 0:2] == 'RE':
									# Recent Weather
									weatherType = 'RecentWeather'
									val = self.decodeWeatherObscuration( value[ 2:])
								else:
									if forecastConditions:
										# Forecast Weather
										weatherType = 'ForecastWeather'
									else:
										# Present Weather
										weatherType = 'PresentWeather'
									
									val = self.decodeWeatherObscuration( value)
								
								# Save if all accounted for
								if val:
									obs[ weatherType].append( val)
									# Identify whether snow is falling
									if 'snow' in val.lower():
										obs[ 'SnowFall'] = 1
								else:
									# All else fails, indicate the decode failed
									success = False
						
						# OK to get next item?
						if getNext:
							value = self.getNext( success)
							valLen = len(value)
					
					# Compute overall decoding success
					obs[ '%ObsDecoded'][ 'Overall'] = int( float(self.decoded) / float(len(self.data)) * 100)
					# Compute decode success of standard observations
					obs[ '%ObsDecoded'][ 'Standard'] = int( float(self.standardDecoded) / float(self.remarkIndex) * 100)
					# Compute decode success of remarks
					if (len(self.data) - self.remarkIndex) > 0:
						obs[ '%ObsDecoded'][ 'Remarks'] = int( float(self.remarksDecoded) / float( len(self.data) - self.remarkIndex) * 100)
		
		return obs
	
	####################################################
	# Decode Automated Maintenance Data - Temp reading #
	# Structured as 'xyyy', where:                     #
	#   'x' = Sign, '0' is pos and '1' is neg          #
	# 'yyy' = Degree Celsius in tenths (21.5 = 215)    #
	# Return resulting float value                     #
	####################################################
	
	def decodeAutoMaintTemp( self, value):
		val = float( value[ 1:]) / 10
		if value[0] == '1':
			val *= -1
		return val
	
	#####################################
	# Decode Wind Condition detail from #
	# String containing coded values.   #
	# Return resulting Dict (if any)    #
	#####################################
	
	def decodeWindConditions( self, value):
		valLen = len( value)
		
		wind = {
			#'Direction': [0,'degrees']	# May also include '[from][to]' if variable
			#'Speed': [0, 'kmh']
			#'Gust': [0, 'kmh']
			#'Chill': [0, 'celsius'] - added later
		}
		
		# Get Wind direction
		if value[ 0:3].isdigit() and int( value[ 0:3]) > 0:
			wind['Direction'] = [int( value[ 0:3]), 'degrees']
		
		# Get Wind Speed Units, 'KT(S)' or 'MPS' or 'KMH'
		offset = valLen - 3
		if value[ offset].isdigit():
			# Indicator is 2 characters, not 3
			offset += 1
		units = value[ offset:valLen]
		
		if units.startswith( 'KT'):
			units = 1.852 # Knots to Kilometers/hr
		elif units == 'MPS':
			units = 3.6 # Meters/sec to Kilometers/hr
		else:
			units = 1 # Kilometers/hr
		
		# Break out Wind Speed and Gust, dropping off leading and trailing detail
		values = value[ 3:offset].split('G')
		
		# Get Wind speed
		if values[0].isdigit():
			wind['Speed'] = [int( round( float( values[0]) * units)), 'kmh']
		
		# Check for Wind Gusts
		if len(values) == 2 and values[1].isdigit():
			wind['Gust'] = [int( round( float( values[1]) * units)), 'kmh']
		
		# Check for optional Wind Variability
		values = self.peekNext().split('V')
		if len(values) == 2 and values[0].isdigit() and values[1].isdigit():
			From = int( values[0])
			To = int( values[1])
			
			if 'Direction' not in wind:
				wind['Direction'] = [0, 'degrees']
			
			wind['Direction'].append( From)
			wind['Direction'].append( To)
			
			if wind['Direction'][0] == 0:
				# Compute general bearing
				if To < From:
					To += 360
				wind['Direction'][0] = From + (float(To - From) / 2)
				if wind['Direction'][0] > 360:
					wind['Direction'][0] -= 360
			self.getNext()	# Pop 'peeked' item from list
		
		return wind
	
	###################################
	# Decode Cloud Cover details from #
	# String containing coded values. #
	# Return resulting phrase (if any)#
	###################################
	
	def decodeCloudCover( self, value):
		desc = ''
		height = ''
		type = ''
		
		valLen = len(value)
		valOff = 0
		
		if value[ 0:3] in self.coverage:
			valOff = 3
			desc = self.coverage[ value[ 0:3]]
		elif value[ 0:2] in self.coverage and valLen == 5:
			valOff = 2
			desc = self.coverage[ value[ 0:2]]
		
		# Check for Height
		if valLen >= 5:
			if value[ valOff:(valOff + 3)].isdigit():
				# Convert Height to meters
				val = float( value[ valOff:(valOff + 3)]) * 30.48
				if val >= 1000:
					# Round to nearest hundreds
					val = int( round( val / 100) * 100)
				else:
					# Round to nearest tens
					val = int( round( val / 10) * 10)
				height = " at {0}m".format( val)
		
		# Check for Type
		if value.endswith( 'CB'):
			type = " " + self.remarks[ 'CB']
		elif value.endswith( 'TCU'):
			type = " " + self.remarks[ 'TCU']
		else:
			type = " clouds"
		
		return (desc.format( type) + height)

	#########################################
	# Decode Total Cloud Cover details from #
	# String containing coded values.       #
	# Return resulting percentage           #
	#########################################
	
	def decodeTotalCloudCover( self, value):
		val = 0
		if value[ 0:3] in self.totalCloudCover:
			val = self.totalCloudCover[ value[ 0:3]]
		return val		
	
	#####################################
	# Decode Cloud Ceiling height from  #
	# String containing 3 digit number. #
	# Return resulting height in m      #
	#####################################
	
	def decodeCloudCeiling( self, value):
		desc = ''
		height = None
		type = ''
		
		valLen = len(value)
		valOff = 0
		
		if value[ 0:3] in self.coverage:
			valOff = 3
			desc = self.coverage[ value[ 0:3]]
		elif value[ 0:2] in self.coverage and valLen == 5:
			valOff = 2
			desc = self.coverage[ value[ 0:2]]
		
		# Check for Height
		if valLen >= 5:
			if value[ valOff:(valOff + 3)].isdigit():
				# Convert Height to meters
				val = float( value[ valOff:(valOff + 3)]) * 30.48
				if val >= 1000:
					# Round to nearest hundreds
					val = int( round( val / 100) * 100)
				else:
					# Round to nearest tens
					val = int( round( val / 10) * 10)
				# Cloud ceiling is the lowest BKN or OVC layer
				if value[ 0:3] == 'BKN' or value[ 0:3] == 'OVC':
					height = val
		
		return height

	######################################
	# Decode Weather Obscuration details #
	# from String containg coded values. #
	# Return resulting phrase (if any)   #
	######################################
	
	def decodeWeatherObscuration( self, value):
		if not value:
			return ''
		
		intensity = ''
		proximity = ''
		descriptor = ''
		phenomenon = ''
		
		sep = ''
		
		offset = 0
		length = len(value)
		
		if (offset + 3) <= length:
			# Check (optional) Intensity: 1
			if value[ offset] in self.intensity:
				# Check for Well-developed...
				if value[ offset:(offset + 3)] in self.other:
					phenomenon = self.other[ value[ offset:(offset + 3)]]
					sep = ' and '	# Prep for additional Phenomenons
					offset += 3
				else:
					# nope, use standard intensity
					intensity = self.intensity[ value[ offset]] + " "
					offset += 1
		
		if (offset + 2) <= length:
			# Check (optional) Proximity: 2
			if value[ offset:(offset + 2)] in self.proximity:
				proximity = " " + self.proximity[ value[ offset:(offset + 2)]]
				offset += 2
		
		if (offset + 2) <= length:
			# Check (optional) Descriptor: 3
			if value[ offset:(offset + 2)] in self.descriptor:
				descriptor = self.descriptor[ value[ offset:(offset + 2)]]
				offset += 2
		
		# Check other Phenomenon
		while (offset + 2) <= length:
			val = value[ offset:(offset + 2)]
			
			if val in self.precipitation:
				val = intensity + self.precipitation[ val]
				intensity = ''
				if descriptor:
					if value[ (offset - 2):(offset + 2)] in self.conjunction:
						val = self.conjunction[ value[ (offset - 2):(offset + 2)]] + " " + val
			elif val in self.obscuration:
				val = self.obscuration[ val]
			elif val in self.other:
				val = self.other[ val]
			else:
				break
			
			if descriptor:
				val = " " + val
			
			phenomenon += sep + descriptor + val
			descriptor = ''
			sep = ' and '
			offset += 2
		
		# Decode all or nothing!
		if offset == length:
			return (descriptor + phenomenon + proximity).strip()
		else:
			return ''

###################
# Show Usage help #
###################

def usage( help=False):
	
	"""
Command-line usage: '{0} [-v] [-h] [-d] [-c] [<str> ...]'

     '-v' = [optional] Turn Verbose option on.
     '-h' = [optional] Display detailed help.
     '-d' = [optional] Download and Decode Metar content.
     '-c' = [optional] Use Current observation cycle plus last full cycle.
    <str> = [optional] Item 'text' or ICAO station to search for
            and then display details on. Implies '-d' option.
            Can also specify a single string containing:
             'Skipped' = To display details for skipped record(s)
            'Standard' = Show text of 'Standard' item(s) not decoded
              'Remark' = Show text of 'Remark' item(s) not decoded
      ... = Additional 'text' or station ids to search for.
"""

	fileName = os.path.split( __file__)[1]
	title = "\n{0}, {1}:".format( fileName, MetarReader.version)
	
	print title
	print "-" * (len(title) - 1)
	
	if help:
		print MetarReader.__doc__
		print "\n----"
	
	print usage.__doc__.format( fileName)

#####################
# Handle direct run #
#####################

if __name__ == "__main__":
	verbose = False
	decode = False
	cycle = False
	
	# Read Args from right to left, dropping as needed
	for index in range( len(sys.argv) - 1, 0, -1):
		if sys.argv[ index] == '-v':
			verbose = True
			del sys.argv[ index]
		elif sys.argv[ index] == '-h':
			usage( True)
			sys.exit()
		elif sys.argv[ index] == '-d':
			decode = True
			del sys.argv[ index]
		elif sys.argv[ index] == '-c':
			cycle = True
			del sys.argv[ index]
	
	if decode or len(sys.argv) > 1:
		Metar = MetarReader( verbose, False, cycle)
		if len(sys.argv) > 1:
			Metar.decode( sys.argv[1:])
		else:
			Metar.decode()
		sys.exit()
	else:
		usage()
