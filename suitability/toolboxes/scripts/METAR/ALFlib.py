
#########################################################
#       ALFlib.py - Aggregated Live Feed library        #
#                                                       #
# A collection of helper utilitiy classes and functions #
# that assist Live Data Aggregation scripts.            #
#                                                       #
# Created by: Paul Dodd - esri, Technical Marketing     #
#     Build: v1.1.0, May 2012, P.D.                     #
#         - Added minVersion function logic.            #
#         - Added AppLock class logic.                  #
#         - Update Logger to Lock Pre-mature exit file  #
#           to overcome mutli-instance execution.       #
#           Supports graceful exit if more than one     #
#           instance attempts to run at the same time.  #
#           Revised Pre-mature exit detection logic to  #
#           deal with Lock file and parallel executions.#
#           Added keepActivity logic to allow saving    #
#           Log file when activity logging is needed.   #
#     Build: v1.0.3, Apr 2012, P.D.                     #
#         - Restructured code to better adhere to       #
#           Python standards and best practices.        #
#         - Version details available from namespace    #
#     Build: v1.0.2, Apr 2012, P.D.                     #
#         - Patched: 'CountryCodeLoader' and            #
#                    'WeatherStationLoader' to bubble   #
#                    up exceptions.                     #
#         - Updated: Base class '_CacheLoader' to       #
#                    accept and test for an Alternate   #
#                    source URL.                        #
#     Build: v1.0.1, Apr 2012, P.D.                     #
#     Build: v1.0.0, Mar 2012, P.D.                     #
#                                                       #
# Depends on: Python v2.6+                              #
#########################################################

import atexit, datetime, errno, os, sys, tempfile, time, traceback, urllib2
import ALFlib as utils
from fnmatch import fnmatch

# Version details directly available from namespace, as of v1.0.3
major = 1
minor = 1
bug = 0
desc = "v{0}.{1}.{2}, May 2012, Paul Dodd - esri".format( major, minor, bug)

# Version function, for compatability
def version():
	"""Function: version()

    Report version details for this library.

    Returns Dictionay that includes:
    {'Major': <num>, 'Minor': <num>, 'Bug': <num>, 'Desc': <description>}

    Properties also available from this library directly via <library>.<property>:
        'major' Gets the Major release number.
        'minor' Gets the Minor release number.
          'bug' Gets the Bug fix level of release.
         'desc' Gets the release description.
"""

	return { "Major": major, "Minor": minor, "Bug": bug, "Desc": desc}

# Report if ALFlib version is at least the requested minimum, new at v1.1.0
def minVersion( major=0, minor=0, bug=0):
	"""Function: minVersion( <major>, <minor>, <bug>)

    return True if this library version is at least the minimum
    specified by the input provided. False otherwise.

    Where:
        <major> = Major release number is at least this number.

        <minor> = And, Minor release number is at least this number.

          <bug> = And, Bug release number ia at least this number.
"""

	if major and type(major) == type("") and major.isdigit():
		major = int(major)

	if minor and type(minor) == type("") and minor.isdigit():
		minor = int(minor)

	if bug and type(bug) == type("") and bug.isdigit():
		bug = int(bug)

	try:
		return (utils.major > major or (utils.major == major and \
			(utils.minor > minor or (utils.minor == minor and utils.bug >= bug))))
	except:
		return False

######################
# Assorted Constants #
######################

class Constants( object):
	"""Class: Constants()

    Assorted Constants.

        'TrueNorth': Dictionary x-ref of Text Bearing ('N', 'S', 'SW',
                     'SSW', ...) to matching decimal degree.
"""
	
	# True-North direction to degree x-ref. Paul Dodd, Mar 2012
	TrueNorth = {
		'N': 0,		# North
		'NbE': 11.25,	# North by East
		'NNE': 22.5,	# North, North-East
		'NEbN': 33.75,	# North-East by North
		'NE': 45,		# North-East
		'NEbE': 56.25,	# North-East by East
		'ENE': 67.5,	# East, North-East
		'EbN': 78.75,	# East by North
		'E': 90,		# East
		'EbS': 101.25,	# East by South
		'ESE': 112.5,	# East, South-East
		'SEbE': 123.75,	# South-East by East
		'SE': 135,		# South-East
		'SEbS': 146.25,	# South-East by South
		'SSE': 157.5,	# South, South-East
		'SbE': 168.75,	# South by East
		'S': 180,		# South
		'SbW': 191.25,	# South by West
		'SSW': 202.5,	# South, South-West
		'SWbS': 213.75,	# South-West by South
		'SW': 225,		# South-West
		'SWbW': 236.25,	# South-West by West
		'WSW': 247.5,	# West, South-West
		'WbS': 258.75,	# West by South
		'W': 270,		# West
		'WbN': 281.25,	# West by North
		'WNW': 292.5,	# West, North-West
		'NWbW': 303.75,	# North-West by West
		'NW': 315,		# North-West
		'NWbN': 326.25,	# North-West by North
		'NNW': 337.5,	# North, North-West
		'NbW': 348.75	# North by West
	}

######################################################
# Log File Manager                                   #
#                                                    #
# Overrides sys.stdout, sys.stderr, and sys.exit     #
# handlers. Echos content to Activity and Error logs.#
# Also traps and reports unhandled Exceptions,       #
# retaining error log if non-zero exit code or       #
# exception is detected.                             #
#                                                    #
# Output: Archive log as: <name>_YYYYMM.txt          #
#        Activity log as: <name>_LastRun.txt         #
#           Error log as: <errPath>\YYYYMMDD_HHMI.txt#
#                                                    #
# <name> = NickName used during class instantiation. #
# <errPath> = Folder called '<name>_Errors'          #
#                                                    #
# Build: v1.1.0, May 2012, Paul Dodd - esri          #
#     - Added singleton logic to allow Pre-mature    #
#       Exit file locking and graceful exit when     #
#       detected.                                    #
#     - Added 'keepActivity' property logic.         #
# Build: v1.0.1, Apr 2012, Paul Dodd - esri          #
#     - Restructured code to better adhere to Python #
#       standards and best practices.                #
#     - Improved Exception handling and reporting.   #
# Build: v1.0.0, Mar 2012, Paul Dodd - esri          #
######################################################

class Logger( object):
	
	"""Class: Logger( <nickName>, <homeFolder>, <retention>, <singleton>)

    Initialize new <object> that will manage Log files for any script that
    instantiates this class. Activity Log will contain current run details.
    Archive Logs will contain summary of activity by month. Error Logs will
    contain copy of Activity Log for future review, and only retained if an
    Exception was found or Exit Code != 0. Expired Logs are removed as needed.

    Routine automatically traps Un-handled Exceptions and Script Exits with
    Exit Codes != 0 (logging them to the Archive and Error logs). Routine
    overrides Standard Out and Standard Error handlers, trapping any Printed
    message or reported error, logging all content.

        Where:
              <nickName> = Name of routine that instantiates class. Archive
                           logs, Activity log, and ErrorLog folder will be
                           comprised of this name.

            <homeFolder> = Home location where logs will be created. Must
                           have write access to this location.

             <retention> = Number of months to retain Log Files.
                           (default) is 3, this month plus prior two.

             <singleton> = (True or False) Restrict run to a single instance,
                           gracefully terminating when Pre-mature exit Lock
                           is detected. Exit will set status to -1 if Lock is
                           detected. (default) is False. 

    Methods:
        '<object>.archive( <str>, <boolean>)' Record <str> to Archive Log.

                           <str> = Text to be recorded.
                       <boolean> = True or False, echo <str> content to StdOut
                                   and Activity Log. (default) is False.

        '<object>.resetError()' Reset prior error condition, clearing error
                                detection and reporting at exit.

    Properties:
        From any routine using 'sys' module:
             'sys.stdout.log' True or False, to log messages or not.
            'sys.stdout.echo' True or False, to echo messages to original
                              stream or not.
            (Same properties are available for 'sys.stderr'.)

        Other:
            '<object>.keepActivity' True or False, instructs Logger to save and
                                    re-label the error log for posterity when a
                                    non-error exit is encountered. Appending
                                    '_activity' to the file name. Allowing the
                                    tracking of activity over time by using the
                                    existing log files.
"""
	
	def __init__( self, nickName, home, retention=3, singleton=False):
		home = os.path.realpath( home)
		
		self._keepActivity = False
		
		# Does home exist?
		if not os.access( home, os.F_OK):
			try:
				# Try to create home folder
				os.makedirs( home)
			
			except Exception as e:
				raise IOError( "* Unable to create Log path: '{0}', {1}".format( home, e))
		else:
			# Do we have Write permission?
			if not os.access( home, os.W_OK):
				raise IOError( "* Unable to write to Log path: '{0}'".format( home))
		
		errorFolder = os.path.join( home, nickName + '_Errors')
		
		# Does error log folder exist?
		if not os.access( errorFolder, os.F_OK):
			os.mkdir( errorFolder)
		
		# Check for Pre-mature Exit Detection file
		self._earlyExit = os.path.join( errorFolder, 'PreMatureExitDetection.tmp')
		if os.access( self._earlyExit, os.F_OK):
			earlyExit = datetime.datetime.fromtimestamp( os.stat( self._earlyExit).st_ctime)
			earlyExit = os.path.join( errorFolder, earlyExit.strftime( '%Y%m%d_%H%M.txt'))
		else:
			earlyExit = False
		
		now = datetime.datetime.now()
		# Create Pre-mature Exit file immediately after taking note of date/time
		try:
			self._singleton = utils.AppLock( self._earlyExit)
			if not self._singleton.lock():
				# Not an early exit, prior process still running!
				if singleton:
					# Requested single process execution!
					print " * Unable to Lock Pre-mature exit file, single instance of app requested, exiting!"
					sys.exit(-1)
				else:
					# Turn off singleton, do NOT disturb existing early exit file!
					self._singleton = False
					earlyExit = "Process still running"
		except Exception as e:
			self._singleton = False
			raise Exception( " * Error: Unable to create Application Lock on Pre-mature Exit file: {0}".format( e))
		
		# Setup log names
		self._activityLog = os.path.join( home, nickName + '_LastRun.txt')
		
		archiveFmt = nickName + '_%Y%m.txt'	# Filename Format mask used by DateTime format and Cleanup
		archiveMask = nickName + '_2*.txt'	# Search Mask for Log Cleanup
		self._archiveLog = os.path.join( home, now.strftime( archiveFmt))
		
		errorFmt = '%Y%m%d_%H%M.txt'	# Filename Format mask used by DateTime format and Cleanup
		errorMask = '2*.txt'		# Search Mask for Log Cleanup
		self._errorLog = os.path.join( errorFolder, now.strftime( errorFmt))
		
		# Open Log files
		self._archiveFP = open( self._archiveLog, 'a')
		self._errorFP = open( self._errorLog, 'w')
		self._activityFP = open( self._activityLog, 'w')
		
		# Override StdOut and StdErr
		sys.stdout = self._StdOverride( self._activityFP, sys.stdout, self._errorFP)
		sys.stderr = self._StdOverride( self._activityFP, sys.stderr, self._errorFP)
		
		# Do not echo errors to screen
		sys.stderr.echo = False
		
		# Setup Hooks for Exceptions and Exit
		self._applyHooks()
		
		# Act on Prior Run Pre-mature exit state
		if earlyExit:
			if earlyExit == "Process still running":
				# Note additional process detected
				self.archive( "\n* Note * Detected parallel process running *", True)
			else:
				# Alert to Pre-mature exit
				self.archive( "\n* Detected Pre-mature exit by prior run *", True)
				self.archive( "  For details see: '{0}'".format( earlyExit), False)
		
		# Display startup details
		title = "\n{0} Routine Started: {1}".format( nickName, now.strftime( '%H:%M:%S %a %m/%d/%Y'))
		self.archive( title, True)
		self.archive( '-' * (len(title) - 1), True)
		
		# Cleanup Log Files
		month = now.year * 12 + now.month - retention
		year = month / 12
		month = month - (year * 12) + 1
		ageOut = datetime.datetime( year, month, 1)	# Remove anything older than this
		self._trimLogs( ageOut, home, archiveMask, archiveFmt)
		self._trimLogs( ageOut, errorFolder, errorMask, errorFmt)
	
	@property
	def keepActivity( self):
		return self._keepActivity

	@keepActivity.setter
	def keepActivity( self, value):
		if type(value) == type(True):
			self._keepActivity = value

	def archive(self, message, echo=False):
		self._archiveFP.write(message + '\n')
		if echo:
			print message
	
	def _trimLogs( self, expireDate, logPath, logMask, logFormat):
		# Remove Log files older than 'expireDate' and report deletion to Archive Log
		expireFormat = expireDate.strftime( logFormat)
		
		for file in os.listdir( logPath):
			if fnmatch( file, logMask):
				if file < expireFormat:
					fileName = os.path.join( logPath, file)
					self.archive( " * Deleting Log: '{0}'".format( fileName))
					os.remove( fileName)
	
	def _applyHooks(self):
		# Apply Hooks to Exception and Exit handlers
		def exceptionHook( type, value, tb):
			print "\n* Un-handled Exception Detected *"
			echoWas = sys.stderr.echo
			sys.stderr.echo = True
			
			for line in traceback.format_exception( type, value, tb):
				sys.stderr.write( line)
			sys.stderr.write( '\n')
			
			if not self._exitValue:	# Report error in Archive on first encounter
				self.archive( "* Un-handled Exception Detected, details: '{0}' *".format( self._errorLog))
			
			sys.stderr.echo = echoWas
			self._exitValue = 'Exception'
		
		def exitHook( value=0):
			# Fired before 'atexit' Hook when 'sys.exit' invoked, save Exit value
			self._exitValue = value
			_origExit( value)
		
		def atexitHook():
			# Load Exit value, 'exitHook' not fired if clean exit and 'sys.exit' not invoked
			value = self._exitValue
			
			if self._singleton:
				# Release Application Lock on early exit file
				self._singleton.unlock()
			
			sys.stderr.write( "\nFinished: {0}\n".format( datetime.datetime.now().strftime( '%H:%M:%S %a %m/%d/%Y')))
			
			if value:
				if value == 'Exception':
					return
				
				if isinstance( value, str) or isinstance( value, unicode):
					sys.stderr.write( "\n* Error Exit detected: {0}\n".format( value))
				else:
					print "\n* Error Exit '{0}' detected *".format( value)
				
				self.archive( "* Error Exit detected, details: '{0}' *".format( self._errorLog))
			else:
				# Clean exit, no need to keep Error Log so remove it, unless keep
				# activity has been set to True!
				self._errorFP.close()
				self._errorFP = False

				if not self._keepActivity:
					# Remove it!
					os.remove( self._errorLog)
				else:
					# Rename it!
					path, filename = os.path.split( self._errorLog)
					name, ext = filename.split('.')
					activityFile = os.path.join( path, name + '_activity.' + ext)
					os.rename( self._errorLog, activityFile)
		
		self._exitValue = False			# Set initial Exit value
		_origExit = sys.exit			# Save current Exit handle
		sys.exit = exitHook			# Override Exit handle
		atexit.register( atexitHook)		# Register Exit Hook
		sys.excepthook = exceptionHook	# Override Exception handle

	# Clear or Reset error condition	
	def resetError( self):
		self._exitValue = False
	
	class _StdOverride( object):
		# Class designed to override sys.stdout and sys.stderr (output) handlers
		def __init__(self, fp, origFp, errFp):
			self._fp = fp
			self._origFp = origFp
			self._errFp = errFp
			self.echo = True
			self.log = True
		
		def write(self, string):
			if self.echo:	# Ok to echo to original output?
				if self._origFp and not self._origFp.closed:
					self._origFp.write( string)
			
			if self.log:	# Ok to log to new output?
				if self._fp and not self._fp.closed: 
					self._fp.write( string)
				# Echo to Error Log
				if self._errFp and not self._errFp.closed:
					self._errFp.write( string)
		
		def writelines(self, sequence):
			if self.echo:	# Ok to echo to original output?
				if self._origFp and not self._origFp.closed:
					self._origFp.writelines( sequence)
			
			if self.log:	# Ok to log to new output?
				if self._fp and not self._fp.closed: 
					self._fp.writelines( sequence)
				# Echo to Error Log
				if self._errFp and not self._errFp.closed:
					self._errFp.writelines( sequence)
		
		def flush(self):
			if self._origFp and not self._origFp.closed:
				self._origFp.flush()

############################################################
# AppLock                                                  #
#                                                          #
# Code Source: http://code.activestate.com/recipes/576891/ #
#          By: Max Polk - MIT, Aug 2009                    #
#                                                          #
# Build: v1.0.0, May 2012, Paul Dodd - esri                #
#     - Augmented to support Windows                       #
############################################################

class AppLock( object):
	"""Class: AppLock( <lockFile>)

    Ensures application is running only once by creating a lock file.

    Ensure call to lock is True. Then call unlock at exit to remove
    lock file.

    Where:
        <lockFile> = Path and Name of file to create for lock.

    Methods:
          '<object>.lock()' = Place lock on file. Return True if successful
                              or False if not (another instance has the file).
        '<object>.unlock()' = Remove lock placed on file.

    Remarks:
        You cannot read or write to the lock file, but for some reason
        you can remove it.  Once removed, it is still in a locked state
        somehow.  Another application attempting to lock against the file
        will fail, even though the directory listing does not show the
        file.  Mysterious, but we are glad the lock integrity is upheld
        in such a case.

    Instance variables:
        lockfile  -- Full path to lock file
        lockfd    -- File descriptor of lock file exclusively locked
"""

	def __init__ (self, lockfile):
		self.lockfile = lockfile
		self.lockfd = None

	def lock (self):
		"""
            Creates and holds on to the lock file with exclusive access.
            Returns True if lock successful, False if it is not, and raises
            an exception upon operating system errors encountered creating the
            lock file.
            """

		try:
			import fcntl
			self._windows = False
		except:
			self._windows = True

		try:
			#
			# Create or else open and trucate lock file, in read-write mode.
			#
			# A crashed app might not delete the lock file, so the
			# os.O_CREAT | os.O_EXCL combination that guarantees
			# atomic create isn't useful here.  That is, we don't want to
			# fail locking just because the file exists.
			#
			# Could use os.O_EXLOCK, but that doesn't exist yet in my Python
			#
			if self._windows and os.access( self.lockfile, os.F_OK):
				os.remove( self.lockfile)	# Should fail if in use!

			self.lockfd = os.open (self.lockfile,
				os.O_TRUNC | os.O_CREAT | os.O_RDWR)

			if not self._windows:
				# Acquire exclusive lock on the file, but don't block waiting for it
				fcntl.flock (self.lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)

				# Writing to file is pointless, nobody can see it
				os.write (self.lockfd, "My Lockfile")

			return True

		except (OSError, IOError), e:
			# Lock cannot be acquired is okay, everything else reraise exception
			if e.errno in (errno.EACCES, errno.EAGAIN):
				return False
			else:
				raise

	def unlock (self):
		try:
			# FIRST unlink file, then close it.  This way, we avoid file
			# existence in an unlocked state. Except for Windows, need to close first!
			if self._windows:
				os.close(self.lockfd)
			
			os.unlink (self.lockfile)

			# Just in case, let's not leak file descriptors
			os.close (self.lockfd)

		except (OSError, IOError), e:
			# Ignore error destroying lock file.  See class doc about how
			# lockfile can be erased and everything still works normally.
			pass


####################################################
# Generic stub class providing common data Caching #
# features for data specific to other Classes.     #
#                                                  #
# Maintains a sorted List of Dictionary items.     #
#                                                  #
# Output: Local cache file updated once daily.     #
#         Cache file stored in System Temp folder. #
#                                                  #
# Build: v1.0.1, Apr 2012, Paul Dodd - esri        #
#     - Restructured code to better adhere to      #
#       Python standards and best practices.       #
# Build: v1.0.0, Feb 2012, Paul Dodd - esri        #
####################################################

class _CacheLoader( object):
	
	# Test Cache file to see if it needs to be reloaded, True if modified date of file is not today
	def loadRequired( self):
		# Check existance of Cached content
		if os.access( self.fileName, os.R_OK):
			fromtimestamp = datetime.date.fromtimestamp
			today = time.time()
			
			# Check if refresh required
			if fromtimestamp( os.stat( self.fileName).st_mtime) == fromtimestamp( today):
				return False
		
		return True
	
	# Download and save URL content to file
	def _download( self, url, fileName):
		iFP = urllib2.urlopen( url)
		oFP = open( fileName, 'w')
		
		line = iFP.readline()
		while line:
			oFP.write( line)
			line = iFP.readline()
		
		iFP.close()
		oFP.close()
	
	def loadData( self):
		fileName = self.fileName
		fileNameOld = fileName + '.old'
		url = self.dataSource
		
		try:
			# Need to Download new content?
			if self.loadRequired():
				# Save existing file
				if os.access( fileName, os.F_OK):
					if os.access( fileNameOld, os.F_OK):
						os.remove( fileNameOld)
					os.rename( fileName, fileNameOld)
				
				try:
					# Yes, download!
					self._download( url, fileName)
				
				except Exception as e:
					if hasattr( self, 'dataAlternate'):
						# Try Alternate data source if exist
						sys.stderr.write( "\n * Using Alternate data source * Failed to load Primary from:\n   '{0}',\n   {1}\n".format( url, e))
						url = self.dataAlternate
						self._download( url, fileName)
					else:
						raise e
			
			# Clear List and Dict
			self.itemList = []
			self.itemDict.clear()
			
			# Return open file handle
			return open( fileName, 'rt')
		
		except Exception as e:
			
			# Check for old copy of cached file
			if os.access( fileNameOld, os.F_OK):
				# Clear current cache file if exists
				if os.access( fileName, os.F_OK):
					os.remove( fileName)
				
				# Restore old copy
				os.rename( fileNameOld, fileName)
				sys.stderr.write( "\n * Using Fallback Cache * Failure in Cache 'loadData' routine, cannot update from:\n   '{0}',\n   {1}\n".format( url, e))
				
				# Return open file handle
				return open( fileName, 'rt')
			else:
				raise Exception( " * Failure in Cache 'loadData' routine, cannot update from:\n  '{0}',\n   {1}".format( url, e))
	
	# Add item to ordered Dictionary cache
	def _addData( self, key, value):
		if key not in self.itemDict:
			# Add key to ordered list
			self.itemList.append( key)
		
		# Add item to indexed list
		self.itemDict[ key] = value
		
		# Return item
		return self.itemDict[ key]
	
	# Sort data
	def _sortData( self):
		self.itemList.sort()
	
	# Report if item is in Dictionary cache
	def __contains__( self, item):
		return (item in self.itemDict)
	
	# Get item or indexed item from Dictionary cache
	def __getitem__( self, item):
		if isinstance( item, int) or isinstance( item, long):
			if item < 0 or item >= len( self.itemList):
				raise IndexError( item)
			else:
				return self.itemDict[ self.itemList[ item]]
		
		if not item in self.itemDict:
			raise KeyError( item)
		else:
			return self.itemDict[ item]
	
	# Return number of items in Dictionary cache
	def __len__( self):
		return len( self.itemList)

	# Initialize, specifying name of file to maintain
	def __init__( self, fileName):
		scriptName = os.path.split( __file__)[-1]
		
		# Set Cache filename to system temp storage location + script name + fileName
		self.fileName = os.path.join( tempfile.gettempdir(), "{0}_{1}".format( scriptName.split( ".")[0], fileName))
		
		# Setup Dictionary cache storage
		self.itemList = []
		self.itemDict = {}

####################################################################
# Load Country Code/Description cross reference data. Maintains an #
# internal List sorting items by selected 'indexOn' field order.   #
#                                                                  #
# Source: ftp://ftp.fu-berlin.de/doc/iso/iso3166-countrycodes.txt  #
#                                                                  #
# Data Dict cache: <countryName>, <abbr2>, <abbr3>, <countryCode>  #
#                                                                  #
# 'indexOn' property controls which data Field to index Dict on    #
#     (default) None = Do not initially load data                  #
#                  1 = Country code                                #
#                  2 = 2-digit abbreviation                        #
#                  3 = 3-digit abbreviation                        #
#                                                                  #
# Build: v1.0.1, Apr 2012, Paul Dodd - esri                        #
#     - Restructured code to better adhere to Python standards and #
#       best practices.                                            #
# Build: v1.0.0, Feb 2012, Paul Dodd - esri                        #
####################################################################

class CountryCodeLoader( _CacheLoader):
	
	"""Class: CountryCodeLoader( <indexOn>)

    Initialize new <object> and load Country Name cross reference data,
    ordering items by desired field index.

        Where <indexOn> can be:
            (default) None = Init only, do not load data. Must manually
                             invoke 'loadData' method to initiate data load.
                         1 = Index items by Country Code field
                         2 = Index items by 2-digit abbreviation field
                         3 = Index items by 3-digit abbreviation field

    Dictionary items are stored in the form of:
        {'Name': 'UNITED STATES', 'Code': '840', 'Abbr2': 'US', 'Abbr3': 'USA'}

    Methods:
        '<object>.loadData( <indexOn>)' Sets field index and loads data, or
                                        re-indexes data if already loaded.
        '<object>.loadRequired()' Returns True if data load has not been done
                                  or if data has not been refreshed today.

    Properties:
        '<object>.fileName' Get name of cache file.
        '<object>.dataSource' Get URL source of data.
        '<object>.indexOn' Get or Sets field index value.

    Data lookup:
        '<object>[ <index>]' Where <index> = 0 to 'len( <object>)' - 1
        '<object>[ <str>]' Where <str> = value related to index field chosen.

    Use: 'if <str> in <object>' to query existance of a specific item.
         'for item in <object>' to iterate through indexed content.
         'len( <object>)' to query for total number of items.
"""
	
	def __init__( self, indexOn=None):
		# Init base
		super( CountryCodeLoader, self).__init__( "CountryXref.txt")
	
		# Set URL Source location of data
		self.dataSource = "ftp://ftp.fu-berlin.de/doc/iso/iso3166-countrycodes.txt"
		
		# Set indexing
		self.indexOn = indexOn
		
		# Load if index is not None
		if indexOn:
			self.loadData()
	
	def loadData( self, indexOn=None):
		try:
			if indexOn:
				self.indexOn = indexOn
			else:
				indexOn = self.indexOn
			
			# Initiate common download logic, returning file handler
			iFP = super( CountryCodeLoader, self).loadData()
			
			# Parse data if index has been set
			if indexOn:
				# Reset value to word index of incoming data rows
				indexOn -= 1
				if indexOn == 0:
					indexOn = 3
				
				# Setup flags
				line = " "
				start = False
				
				# Start reading data
				while line:
					line = iFP.readline()
					
					# Has to be greater than 9 characters, 1+2+3+3 minimum for all fields
					if len(line) > 9:
						if line[0] == '-':
							start = True
						elif start:
							rowData = line.rsplit( None, 3)
							
							# Add data ( Key, Value)
							self._addData( rowData[ indexOn], {
								"Name": rowData[0],
								"Abbr2": rowData[1],
								"Abbr3": rowData[2],
								"Code": rowData[3]
							})
				
				self._sortData()
			
			iFP.close()
		
		except Exception as e:
			raise Exception( " * Error Loading Country Codes: {0}".format( e))
	
	@property
	def indexOn( self):
		return self._indexOn

	@indexOn.setter
	def indexOn( self, value):
		# Verify property value
		if not (value == None or isinstance( value, int)):
			raise TypeError( "Invalid data Type '{0}'!".format( type( value)))
		
		if value and (value < 1 or value > 3):
			raise AttributeError( "Value out of Range!")
		
		self._indexOn = value

####################################################################
# Load Weather Station reference data. Maintains an internal List  #
# sorting items by selected 'indexOn' field order.                 #
#                                                                  #
# Source:                                                          #
# http://www.aviationweather.gov/static/adds/metars/stations.txt   #
# (alt) http://weather.rap.ucar.edu/surface/stations.txt           #
#                                                                  #
# 'indexOn' property controls which data Field to index Dict on.   #
#     (default) None = Do not initially load cache                 #
#                  1 = ICAO international ID                       #
#                  2 = IATA (FAA) ID                               #
#                  3 = SYNOP international ID number               #
#                                                                  #
# Build: v1.0.1, Apr 2012, Paul Dodd - esri                        #
#     - Restructured code to better adhere to Python standards and #
#       best practices.                                            #
# Build: v1.0.0, Feb 2012, Paul Dodd - esri, Technical Marketing   #
####################################################################

class WeatherStationLoader( _CacheLoader):
	
	"""Class: WeatherStationLoader( <indexOn>)

    Initialize new <object> and load Weather Station reference data,
    ordering items by desired field index.

        Where <indexOn> can be:
            (default) None = Init only, do not load data. Must manually
                             invoke 'loadData' method to initiate data load.
                         1 = Index items by ICAO international ID field
                         2 = Index items by IATA (FAA) ID field
                         3 = Index items by SYNOP international ID field

    Dictionary items are stored in the form of:
        {'Name': 'JACKSONVILLE', 'Province': 'FLORIDA', 'Country':
         'UNITED STATES', 'ICAO': 'KJAX', 'IATA': 'JAX', 'SYNOP': 72206,
         'Longitude': -81.6833333337, 'Latitude': 30.5, 'Elevation': '10m',
         'LastUpdated': '10-FEB-12', 'PlotPriority': 0

         * Note * If attribute flags are present, item may also include:

         'Mflag': <char> if 'M' flag value unknown, or
             'METAR': True
         'Nflag': <char> if 'N' flag value unknown, or
             'NEXRAD': True
         'Vflag': <char> if 'V' flag value unknown, or
             'AIRMET': True, 'SIGMET': True, 'ARTCC': True, 'TAF': True
         'Uflag': <char> if 'U' flag value unknown, or
             'RAWINSONDE': True, 'WINDPROFILER': True
         'Aflag': <char> if 'A' flag value unknown, or
             'ASOS': True, 'AWOS': True, 'MESO': True,
             'HUMAN': True, 'AUGMENTED': True
         'Cflag': <char> if 'C' flag value unknown, or
             'WFO': True, 'RFC': True, 'NCEP': True
        }

    Methods:
        '<object>.loadData( <indexOn>)' Sets field index and loads data, or
                                        re-indexes data if already loaded.
        '<object>.loadRequired()' Returns True if data load has not been done
                                  or if data has not been refreshed today.

    Properties:
        '<object>.fileName' Get name of cache file.
        '<object>.dataSource' Get URL source of data.
        '<object>.indexOn' Get or Sets field index value.

    Data lookup:
        '<object>[ <index>]' Where <index> = 0 to 'len( <object>)' - 1
        '<object>[ <str>]' Where <str> = value related to index field chosen.

    Use: 'if <str> in <object>' to query existance of a specific item.
         'for item in <object>' to iterate through indexed content.
         'len( <object>)' to query for total number of items.
"""
	
	def __init__( self, indexOn=None):
		# Init base
		super( WeatherStationLoader, self).__init__( "StationXref.txt")
		
		# Set URL to Source location of data
		self.dataSource = "http://www.aviationweather.gov/static/adds/metars/stations.txt"
		self.dataAlternate = "http://weather.rap.ucar.edu/surface/stations.txt"
		# old alt: "http://www.rap.ucar.edu/weather/surface/stations.txt"
		
		# Set indexing
		self.indexOn = indexOn
		
		# Load Country Xref
		self.countryCodes = CountryCodeLoader(2)
		
		# Load if index is not None
		if indexOn:
			self.loadData()
	
	def loadData( self, indexOn=None):
		try:
			if indexOn:
				self.indexOn = indexOn
			else:
				indexOn = self.indexOn
			
			# Initiate common download logic, returning file handler
			iFP = super( WeatherStationLoader, self).loadData()
			
			# Parse data if index has been set
			if indexOn:
				# Reset value to word index of incoming data rows
				indexOn += 1
				
				# Setup flags
				line = " "
				lastCountry = "" # Could be State/Province/ or Country name
				lastUpdated = "" # Last date content was updated as: DD-MMM-YY
				
				# Start reading data
				while line:
					line = iFP.readline()
					
					# Has to be greater than 9 characters, minimum field length
					if (len(line) > 10) and not (line.startswith( '!') or line.startswith( 'CD  STATION')):
						if len(line) < 84:
							newCountry = line.rsplit(None, 1)
							
							if newCountry[1].count('-') == 2:
								# State/Province/or Country record
								lastCountry = newCountry[0]
								lastUpdated = newCountry[1]
						else:
							# Station record
							rowData = [
								line[  0:2].strip(), # CD = 2 letter state (province) abbreviation
								line[ 3:19].strip(), # STATION = 16 character station long name
								line[20:24].strip(), # ICAO = 4-character international id
								line[26:29].strip(), # IATA = 3-character (FAA) id
								self.toInt(line[32:37]), # SYNOP = 5-digit international synoptic number
								utils.dms2dd( line[39:41], line[42:44], None, line[44]), # LAT = Latitude (degrees minutes)
								utils.dms2dd( line[47:50], line[51:53], None, line[53]), # LON = Longitude (degree minutes)
								self.toInt(line[55:59]), # ELEV = Station elevation (meters)
								line[   62].strip(), # M = METAR reporting station.   Also Z=obsolete? site
								line[   65].strip(), # N = NEXRAD (WSR-88D) Radar site
								line[   68].strip(), # V = Aviation-specific flag (V=AIRMET/SIGMET end point, A=ARTCC T=TAF U=T+V)
								line[   71].strip(), # U = Upper air (rawinsonde=X) or Wind Profiler (W) site
								line[   74].strip(), # A = Auto (A=ASOS, W=AWOS, M=Meso, H=Human, G=Augmented) (H/G not yet impl.)
								line[   77].strip(), # C = Office type F=WFO/R=RFC/C=NCEP Center
								self.toInt(line[79]),# Digit that follows is a priority for plotting (0=highest)
								line[81:83].strip()  # Country code (2-char) is last column
							]
							
							if rowData[ indexOn]: # Ignore rows with null index field values
								# Update elevation
								if rowData[7]:
									rowData[7] = "{0}m".format( rowData[7])
								
								# Add data ( Key, Value) and complete field updates
								newItem = self._addData( rowData[ indexOn], {
									"LastUpdated": lastUpdated,
									"Name": rowData[1],
									"ICAO": rowData[2],
									"IATA": rowData[3],
									"SYNOP": rowData[4],
									"Latitude": rowData[5],
									"Longitude": rowData[6],
									"Elevation": rowData[7],
									"PlotPriority": rowData[14]
								})
								
								# Add province and country
								if rowData[15] and rowData[15] in self.countryCodes:
									# Country code exists, use it
									newItem['Country'] = self.countryCodes[ rowData[15]]['Name']
									
									# Set province
									if lastCountry != newItem['Country']:
										newItem['Province'] = lastCountry
									else:
										newItem['Province'] = None
								else:
									# No country code, use last
									newItem['Country'] = lastCountry
									newItem['Province'] = None
								
								# M = METAR reporting station.   Also Z=obsolete? site
								if rowData[8] and rowData[8] != 'Z':
									if rowData[8] == 'X':
										newItem['METAR'] = True
									else:
										newItem['Mflag'] = rowData[8]
								
								# N = NEXRAD (WSR-88D) Radar site
								if rowData[9] and rowData[9] != 'Z':
									if rowData[9] == 'X':
										newItem['NEXRAD'] = True
									else:
										newItem['Nflag'] = rowData[9]
								
								# V = Aviation-specific flag (V=AIRMET/SIGMET end point, A=ARTCC T=TAF U=T+V)
								if rowData[10] and rowData[10] != 'Z':
									if rowData[10] == 'T':
										newItem['TAF'] = True
									elif rowData[10] == 'U':
										newItem['AIRMET'] = True
										newItem['SIGMET'] = True
										newItem['TAF'] = True
									elif rowData[10] == 'V':
										newItem['AIRMET'] = True
										newItem['SIGMET'] = True
									elif rowData[10] == 'A':
										newItem['ARTCC'] = True
									else:
										newItem['Vflag'] = rowData[10]
								
								# U = Upper air (rawinsonde=X) or Wind Profiler (W) site
								if rowData[11] and rowData[11] != 'Z':
									if rowData[11] == 'X':
										newItem['RAWINSONDE'] = True
									elif rowData[11] == 'W':
										newItem['WINDPROFILER'] = True
									else:
										newItem['Uflag'] = rowData[11]
																
								# A = Auto (A=ASOS, W=AWOS, M=Meso, H=Human, G=Augmented) (H/G not yet impl.)
								if rowData[12] and rowData[12] != 'Z':
									if rowData[12] == 'A':
										newItem['ASOS'] = True
									elif rowData[12] == 'W':
										newItem['AWOS'] = True
									elif rowData[12] == 'M':
										newItem['MESO'] = True
									elif rowData[12] == 'H':
										newItem['HUMAN'] = True
									elif rowData[12] == 'G':
										newItem['AUGMENTED'] = True
									else:
										newItem['Aflag'] = rowData[12]
								
								# C = Office type F=WFO/R=RFC/C=NCEP Center
								if rowData[13] and rowData[13] != 'Z':
									if rowData[13] == 'F':
										newItem['WFO'] = True
									elif rowData[13] == 'R':
										newItem['RFC'] = True
									elif rowData[13] == 'C':
										newItem['NCEP'] = True
									else:
										newItem['Cflag'] = rowData[13]
				
				# Sort list
				self._sortData()
			
			iFP.close()
		
		#except Exception as e:
		except IOError as e:
			raise Exception( " * Error Loading Weather Stations: {0}".format( e))
	
	def toInt( self, value):
		if value and value.strip().isdigit():
			return int( value)
		return None
	
	@property
	def indexOn( self):
		return self._indexOn

	@indexOn.setter
	def indexOn( self, value):
		# Verify property value
		if not (value == None or isinstance( value, int)):
			raise TypeError( "Invalid data Type '{0}'!".format( type( value)))
		
		if value and (value < 1 or value > 3):
			raise AttributeError( "Value out of Range!")
		
		self._indexOn = value

######################################################
# Convert Degrees.Minutes.Seconds to Decimal Degrees #
#                                                    #
# Build: v1.0.1, Apr 2012, Paul Dodd - esri          #
#     - Restructured code to better adhere to Python #
#       standards and best practices.                #
# Build: v1.0.0, Feb 2012, Paul Dodd - esri          #
######################################################

def dms2dd( degrees=None, minutes=None, seconds=None, bearing=None):
	# Convert Degrees, Minutes, and Seconds to Decimal Degrees
	
	"""Function: dms2dd( <degrees>, <minutes>, <seconds>, <bearing>)

    Convert Geographical Coordinates from Degrees.Minutes.Seconds
    to Decimal Degrees, returning a float value.

        Where:
            <degrees> Is angular Degree from -180 to 180 or None
            <minutes> Is angular Minute from 0 to 59 or None
            <seconds> Is angular Second from 0 to 59 or None
            <bearing> Is directional bearing, can be:
                 (default) None = Preserve +- polarity of <degrees>
                'N','n','E','e' = Return Positive value
                'S','s','W','w' = Return Negative value
"""

	dDegrees = 0
	
	try:
		if degrees:
			degrees = float( degrees)
		else:
			degrees = 0
		
		if minutes:
			minutes = abs( float( minutes)) / 60
		else:
			minutes = 0
		
		if seconds:
			seconds = abs( float( seconds)) / 3600
		else:
			seconds = 0
		
		if degrees >= 0:
			dDegrees = degrees + minutes + seconds
		else:
			dDegrees = degrees - minutes - seconds
		
		if bearing:
			if bearing.upper() == "W" or bearing.upper() == "S":
				dDegrees = abs( dDegrees) * -1
			elif bearing.upper() == "E" or bearing.upper() == "N":
				dDegrees = abs( dDegrees)
		
	except:
		pass
	
	return dDegrees

######################################################
# Convert Celsius Temperature to Fahrenheit          #
#                                                    #
# Build: v1.0.1, Apr 2012, Paul Dodd - esri          #
#     - Restructured code to better adhere to Python #
#       standards and best practices.                #
# Build: v1.0.0, Mar 2012, Paul Dodd - esri          #
######################################################

def c2f( tempCelsius):
	# Convert Celsius to Fahrenheit

	"""Function: c2f( <celsius>)

    Convert Celsuis Temperature to Fahrenheit, returning a float value.

        Where:
            <celsius> Is a float or integer temperature in Celsius units.
"""

	return 9.0 / 5.0 * tempCelsius + 32.0

######################################################
# Convert Fahrenheit Temperature to Celsius          #
#                                                    #
# Build: v1.0.1, Apr 2012, Paul Dodd - esri          #
#     - Restructured code to better adhere to Python #
#       standards and best practices.                #
# Build: v1.0.0, Mar 2012, Paul Dodd - esri          #
######################################################

def f2c( tempFahrenheit):
	# Convert Fahrenheit to Celsius

	"""Function: f2c( <fahrenheit>)

    Convert Fahrenheit Temperature to Celsuis, returning a float value.

        Where:
            <fahrenheit> Is the float or integer temperature
                         in Fahrenheit units.
"""

	return 5.0 / 9.0 * (tempFahrenheit - 32.0)

###############################################
# Weather - Compute Heat Index from Celsius   #
# Temperature and Percent Humidity            #
#                                             #
# Build: v1.0.1, Apr 2012, Paul Dodd - esri   #
#     - Restructured code to better adhere to #
#       Python standards and best practices.  #
# Build: v1.0.0, Mar 2012, Paul Dodd - esri   #
###############################################

def heatIndex( tempCelsius, percentHumidity):
	# Compute Heat Index from Temperature and Relative Humidity Percentage
	# Source: https://en.wikipedia.org/wiki/Heat_index

	"""Function: heatIndex( <celsius>, <humidity>)

    Compute Heat Index from Dry-bulb Temperature and Percent Humidity,
    returning a float value in Celsius.

        Where:
             <celsius> Is the float or integer temperature in Celsius.
            <humidity> Is the float or integer Humidity as a percentage.
                       (a humidity of 66.5% is supplied as '66.5' not '.665')
"""
	
	T = c2f( tempCelsius)	# convert to Fahrenheit
	R = percentHumidity
	
	if R >= 40 and T >= 80:
		# Primary Formula Constants, more accurate (+-1.3F) with limited range
		c1 = -42.379
		c2 = 2.04901523
		c3 = 10.14333127
		c4 = -0.22475541
		c5 = -0.0068383
		c6 = -0.05481717
		c7 = 0.00122874
		c8 = 0.00085282
		c9 = -0.00000199
	elif R <= 80 and T >= 70 and T <= 115:
		# Alternate Formula Constants, less accurate (+-3F) with greater range
		c1 = 0.363445176
		c2 = 0.988622465
		c3 = 4.777114035
		c4 = -0.114037667
		c5 = -0.000850208
		c6 = -0.020716198
		c7 = 0.000687678
		c8 = 0.000274954
		c9 = 0
	else:
		# Outside defined limits
		return
	
	# Return value in Celsius
	return f2c( c1 + c2*T + c3*R + c4*T*R + c5*T*T + c6*R*R + c7*T*T*R + c8*T*R*R + c9*T*T*R*R)

######################################################
# Weather - Compute Relative Humidity from Celsius   #
# Temperature and DewPoint                           #
#                                                    #
# Build: v1.0.1, Apr 2012, Paul Dodd - esri          #
#     - Restructured code to better adhere to Python #
#       standards and best practices.                #
# Build: v1.0.0, Mar 2012, Paul Dodd - esri          #
######################################################

def relativeHumidity( tempCelsius, dewPointCelsius):
	# Compute Relative Humidity from Temperature and Dew Point
	# Source: http://www.gorhamschaffler.com/humidity_formulas.htm

	"""Function: relativeHumidity( <temp>, <dewPoint>)

    Compute Relative Humidity from Celsius Temperature and DewPoint,
    returning a percentage value as float.

        Where:
                <temp> Is the float or integer Dry-bulb temperature
                       in Celsius units.
            <dewPoint> Is the float or integer DewPoint temperature
                       in Celsius units.
"""
	
	# Compute Saturation Vapor Pressure in millibars
	Es = 6.11 * pow( 10, 7.5 * tempCelsius / (237.7 + tempCelsius))
	
	# Compute Actual Vapor Pressure in millibars
	E = 6.11 * pow( 10, 7.5 * dewPointCelsius / (237.7 + dewPointCelsius))
	
	return (E / Es) * 100

###############################################
# Weather - Compute Wind Chill Factor from    #
# Celsius Temperature and Wind Speed in Km/h  #
#                                             #
# Build: v1.0.1, Apr 2012, Paul Dodd - esri   #
#     - Restructured code to better adhere to #
#       Python standards and best practices.  #
# Build: v1.0.0, Mar 2012, Paul Dodd - esri   #
###############################################

def windChill( tempCelsius, windSpeedKmh):
	# Compute Wind Chill from Temperature and Wind Speed
	# Using North American Wind Chill Index (Nov 2001)
	# Source: https://en.wikipedia.org/wiki/Wind_chill

	"""Function: windChill( <celsius>, <windKmh>)

    Compute Wind Chill Factor from Temperature and Wind Speed,
    returning a float Temperature value in Celsius.

        Where:
            <celsius> Is the float or integer temperature in Celsius.
            <windKmh> Is the float or integer Wind Speed in Km/h.
"""
	
	Ta = tempCelsius
	V = windSpeedKmh
	
	if Ta > 10:
		# Outside defined limits
		return
	 
	return 13.12 + 0.6215*Ta - 11.37*pow(V, 0.16) + 0.3965*Ta*pow(V, 0.16)

##################################
# Handle display of script usage # 
##################################

def showInventory():
	
	availableClasses = [ Constants, Logger, AppLock, CountryCodeLoader, WeatherStationLoader]
	availableFunctions = [ version, minVersion, dms2dd, c2f, f2c, heatIndex, relativeHumidity, windChill]
	
	verbose = False
	focus = False

	for index in range( 1, len(sys.argv), 1):
		option = sys.argv[index]
		if option == '-h':
			verbose = True
		else:
			for item in availableClasses + availableFunctions:
				if item.__name__ == option:
					focus = option
					verbose = False
	
	title = os.path.split( __file__)[1]
	title = "\n{0}, {1}:".format( title, version()['Desc'])
	
	print title
	print "-" * (len(title) - 1)
	
	if verbose:
		print "\nAvailable Classes and Functions:"
	else:
		print "\nFor additional Help detail, use '-h [<name>]'"

	for cat, cats, availableList in [["Class", "Classes", availableClasses], ["Function", "Functions", availableFunctions]]:
		if not verbose:
			print "\n        Available {0}:\n".format( cats)
	
		for item in availableList:
			help = item.__doc__
			
			if not help:
				help = "{0}: {1}()\n * Help is not available *".format( cat, item.__name__)
			
			if verbose or item.__name__ == focus:
				print "\n-----"
				print help
			else:
				print help.split('\n')[0]

if __name__ == "__main__":
	showInventory()
