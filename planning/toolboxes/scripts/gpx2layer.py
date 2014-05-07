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
# gpx2layer
# GPX (from XML) to layer
# This script will take a GPX file as input and convert it to a featureclass
# INPUTS:  {GPX file (FILE)}
#          {Output Point Feature Class (FEATURECLASS)}
#          {Output Line Feature Class? (BOOLEAN)} - Optional
# OUTPUTS: Output Point Featureclass (FEATURECLASS)
#          Output Line Featureclass  (FEATURECLASS_line) - Optional 
#-------------------------------------------------------------------------------

from xml.etree import ElementTree
from datetime import datetime
import arcpy, string
import re
import sys, os

def trkpt2dict(gpxfile):
    #Generator : for each trkpt return point + all other attributes as a dictionary
   
    TOPOGRAFIX_NS = './/{http://www.topografix.com/GPX/1/1}'        
    TRACKPOINT_NS = TOPOGRAFIX_NS + 'extensions/{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}TrackPointExtension/{http://www.garmin.com/xmlschemas/TrackPointExtension/v1}'
    
    tree = ElementTree.parse(gpxfile)
       
    for node in tree.findall(TOPOGRAFIX_NS + 'trkpt'):
        d = {}
        y = node.attrib.get('lat')
        x = node.attrib.get('lon')
        z = node.find(TOPOGRAFIX_NS + 'ele').text
        ele = node.find(TOPOGRAFIX_NS + 'ele').text
        t = node.find(TOPOGRAFIX_NS + 'time').text      
        # __Extension Try Block__
        # This section useful for extension elements within a given GPX file, for example "hr" (heartrate)
        #try:
        #    hr = node.find(TRACKPOINT_NS + 'hr').text
        #except:
        #    hr = 0
        #     
        #yield results from reading GPX.
        #additional entries should be added to the end if included in above Try block
        yield arcpy.Point(x,y,z), ele, t  #, hr
        
def parse_timestamp(s): 
  #Returns (datetime, tz offset in minutes) or (None, None) 
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
    values = dict((k, int(v)) for k, v in values.iteritems() 
                  if not k.startswith("tz")) 
    try: 
      return datetime(**values), tz 
    except ValueError: 
      pass 
  return None, None 

if __name__ == "__main__":
    
    #Get GPX and Output directory paramaters
    gpxfile = arcpy.GetParameterAsText(0)        
    outFC = arcpy.GetParameterAsText(1)
    
    #TODO: use Describe to get workspace
    outPath = outFC[0:outFC.rfind("\\")]
    outName = outFC[outFC.rfind("\\")+1:len(outFC)]   
      
    try:       
       
        #Create the FC, add appropriate fields
        arcpy.CreateFeatureclass_management(outPath, outName, "POINT", "", "", "ENABLED", 4326)
        arcpy.AddField_management(outFC, "Date_Time", "DATE")
        arcpy.AddField_management(outFC, "Elevation", "DOUBLE")
        #arcpy.AddField_management(outFC, "hr", "TEXT")   #This is an extension field
        #For every extension field added in the try block, insert an appropriate AddField
                      
    except Exception, ErrorDesc:
        arcpy.AddError(str(ErrorDesc))
            
    arcpy.env.workspace = outPath
        
    rows = arcpy.InsertCursor(outFC)

    recComplete = 0    
    
    # walk through each trkpt, create and insert a record into the feature class for each
    for pt, ele, t in trkpt2dict(gpxfile):   # Add in each value within the Extension Try block         
        row = rows.newRow()           
        row.SHAPE = pt
        row.Elevation = ele
        row.Date_Time = parse_timestamp(t)[0]
        #row.hr = hr   #Extension element
        #Add an entry for each additional entry in the Extension Try block within the dictionary
        rows.insertRow(row)
        recComplete += 1
        
        if (recComplete % 2000) == 0:            
            arcpy.AddMessage("Processed " + str(recComplete) + " records.")
           
    #If "Point to Line" is required, create second output of line featureclass
    if arcpy.GetParameter(2) == 1:
        arcpy.PointsToLine_management(outFC, outFC + "_line")                                
        arcpy.SetParameterAsText(3, outFC + "_line")
