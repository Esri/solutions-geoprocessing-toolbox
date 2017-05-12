# Name: Delete old download data

# Description: Deletes old NETCDF files from a directory specified by the user for a time period specified by a user

# Date Edited: 24/03/2015

#----------------------------------------------------------------------------------------------------------------------

#Import Modules

import os, time, sys, arcpy

# Input path from which files should be deleted.

#path = r"C:\MAOW\NetCDFdata"
path = arcpy.GetParameterAsText(0)
#days = 7
days = arcpy.GetParameter(1)

# Get the present time

now = time.time()

# Get the list of files within the directory.

for f in os.listdir(path):

 f = os.path.join(path, f)

#get the last modified time for each of the files and compare this to the date 7 days ago.

 if os.stat(f).st_mtime < now - days * 86400:

  if os.path.isfile(f):

#If the file is older than specified age then delete it.

   os.remove(f)
   #print f
   arcpy.AddMessage(f)

#print "Specified files deleted"
arcpy.AddMessage ("Specified files deleted")







