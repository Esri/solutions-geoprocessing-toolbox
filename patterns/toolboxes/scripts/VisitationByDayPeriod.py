#------------------------------------------------------------------------------
# Copyright 2015 Esri
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
#------------------------------------------------------------------------------
# 
# ==================================================
# VisitationByDayPeriod.py
# --------------------------------------------------
# Built on ArcGIS Pro 1.0
# ==================================================
# 
# Finds the number of minutes of an event spent in
# night (12 AM to 6 AM), morning (6 AM to 12 PM),
# afternoon (12 PM to 5 PM), and evening (5 PM to 12 AM)
#

# IMPORTS ==========================================
import os, sys, traceback, types
from datetime import datetime
from datetime import timedelta
from datetime import time
from datetime import date
import arcpy
from arcpy import env
from arcpy import da

# LOCALS ===========================================
deleteme = [] # intermediate datasets to be deleted
debug = False # extra messaging during development
data = []
dtEtoN = time(0,0,0)  # From Evening to Night
dtNtoM = time(6,0,0)  # From Night to Morning
dtMtoA = time(12,0,0) # From Morning to Afternoon
dtAtoE = time(17,0,0) # From Afternoon to Evening
periodBreaks = [dtEtoN,dtNtoM,dtMtoA,dtAtoE]


# FUNCTIONS ========================================
def timedeltaToMinutes(inTime):
    minutes = None
    #Convert a time duration to minutes
    asSeconds = inTime.total_seconds()
    minutes = int(asSeconds/60)
    if asSeconds % 60 > 0.0: minutes += 1 #round up
    return minutes

# ARGUMENTS ========================================
inFeatures = arcpy.GetParameterAsText(0)
locationIDField = arcpy.GetParameterAsText(1)
arriveTimeField = arcpy.GetParameterAsText(2)
departTimeField = arcpy.GetParameterAsText(3)
outVisitation = arcpy.GetParameterAsText(4)

# MAIN =============================================
try:
    # get/set environment
    env.overwriteOutput = True
    env.outputCoordinateSystem = arcpy.Describe(inFeatures).spatialReference

    # use start and end times from inFeatures
    inFeatureFields = ["OID@",locationIDField,arriveTimeField,departTimeField]
    for rowLocation in da.SearchCursor(inFeatures,inFeatureFields):
        oid = rowLocation[0]
        if debug == True: arcpy.AddMessage("oid: " + str(oid))
        locID = rowLocation[1]
        arrive = rowLocation[2]
        depart = rowLocation[3]
        
        # How much time between arrive and depart?
        duration = depart - arrive
        if debug == True: arcpy.AddMessage("... duration: " + str(duration))
        durationMinutes = timedeltaToMinutes(duration)
        if debug == True: arcpy.AddMessage("... durationMinutes: " + str(durationMinutes))
        daysBetween = duration.days
        
        if depart - arrive <= timedelta(days=0,seconds=0):
            arcpy.AddWarning("OID " + str(oid) + " departure starts before arrival, or at the same time. Skipping row...")
            continue
        
        if depart == None or arrive == None:
            arcpy.AddWarning("OID " + str(oid) + " depart or arrive dates are empty. Skipping row...")
            continue
        
        # What are the dates of the event?
        daysList = []
        for d in range(0,daysBetween + 1): daysList.append(arrive.date() + timedelta(days=d))
        
        # How many periods in those days?
        periodList = []
        for day in daysList:
            for period in periodBreaks:
                periodList.append(datetime.combine(day,period))
        periodList.append(datetime.combine(day + timedelta(days=1),dtEtoN)) # Add midnight of the next day
        
        minutesNight = 0
        minutesMorning = 0
        minutesAfternoon = 0
        minutesEvening = 0
        
        arriveBefore = None
        arriveBeforeDiff = None
        departAfter = None
        departAfterDiff = None
        
        for i in range(0,len(periodList) - 1):
            first = periodList[i]
            second = periodList[i + 1]
            
            # if they are in the same period
            if (first <= arrive < second) and (first <= depart < second):
                diff = timedeltaToMinutes(depart - arrive)
                if first.time() == dtEtoN: minutesNight = minutesNight + diff
                if first.time() == dtNtoM: minutesMorning = minutesMorning + diff
                if first.time() == dtMtoA: minutesAfternoon = minutesAfternoon + diff
                if first.time() == dtAtoE: minutesEvening = minutesEvening + diff
                continue
            
            #Arrival
            if first <= arrive < second:
                #print("arrived between " + str(first) + " and " + str(second))
                arriveBefore = i + 1
                arriveBeforeDiff = timedeltaToMinutes(second - arrive)
                if first.time() == dtEtoN: minutesNight = minutesNight + arriveBeforeDiff
                if first.time() == dtNtoM: minutesMorning = minutesMorning + arriveBeforeDiff
                if first.time() == dtMtoA: minutesAfternoon = minutesAfternoon + arriveBeforeDiff
                if first.time() == dtAtoE: minutesEvening = minutesEvening + arriveBeforeDiff
                
            # Depature
            if first <= depart < second:
                #print("departed between " + str(first) + " and " + str(second))
                departAfter = i
                departAfterDiff = timedeltaToMinutes(depart - first)
                if first.time() == dtEtoN: minutesNight = minutesNight + departAfterDiff
                if first.time() == dtNtoM: minutesMorning = minutesMorning + departAfterDiff
                if first.time() == dtMtoA: minutesAfternoon = minutesAfternoon + departAfterDiff
                if first.time() == dtAtoE: minutesEvening = minutesEvening + departAfterDiff
            
            #In between
            if arrive < first and second < depart:
                diff = timedeltaToMinutes(second - first)
                #print("still there " + str(diff) + " minutes")
                if first.time() == dtEtoN: minutesNight = minutesNight + diff
                if first.time() == dtNtoM: minutesMorning = minutesMorning + diff
                if first.time() == dtMtoA: minutesAfternoon = minutesAfternoon + diff
                if first.time() == dtAtoE: minutesEvening = minutesEvening + diff
        
        #Percentage of total time spent
        pctNight = (float(minutesNight)/float(durationMinutes)) * 100.0
        pctMorning = (float(minutesMorning)/float(durationMinutes)) * 100.0
        pctAfternoon = (float(minutesAfternoon)/float(durationMinutes)) * 100.0
        pctEvening = (float(minutesEvening)/float(durationMinutes)) * 100.0
        
        data.append([oid,locID,arrive,depart,durationMinutes,minutesNight,pctNight,minutesMorning,pctMorning,minutesAfternoon,pctAfternoon,minutesEvening,pctEvening])
    del rowLocation
    
    #create the output table
    arcpy.AddMessage("Creating output structure...")
    arcpy.CreateTable_management(os.path.dirname(outVisitation),os.path.basename(outVisitation))
    arcpy.AddField_management(outVisitation,"source","LONG","#","#","#","Source Table OID")
    arcpy.AddField_management(outVisitation,"locid","TEXT","#","#","#","Location ID")
    arcpy.AddField_management(outVisitation,"arrive","DATE","#","#","#","Arrive Date/Time")
    arcpy.AddField_management(outVisitation,"depart","DATE","#","#","#","Depart Date/Time")
    arcpy.AddField_management(outVisitation,"duration","LONG","#","#","#","Duration (minutes)")
    arcpy.AddField_management(outVisitation,"minNight","LONG","#","#","#","Night (minutes)")
    arcpy.AddField_management(outVisitation,"pctNight","DOUBLE",6,2,"#","Night (% duration)")
    arcpy.AddField_management(outVisitation,"minMorn","LONG","#","#","#","Morning (minutes)")
    arcpy.AddField_management(outVisitation,"pctMorn","DOUBLE",6,2,"#","Morning (% duration)")
    arcpy.AddField_management(outVisitation,"minAfter","LONG","#","#","#","Afternoon (minutes)")
    arcpy.AddField_management(outVisitation,"pctAfter","DOUBLE",6,2,"#","Afternoon (% duration)")
    arcpy.AddField_management(outVisitation,"minEven","LONG","#","#","#","Evening (minutes)")
    arcpy.AddField_management(outVisitation,"pctEven","DOUBLE",6,2,"#","Evening (% duration)")
    
    # fill the table
    fields = ["source","locid","arrive","depart","duration","minNight","pctNight","minMorn","pctMorn","minAfter","pctAfter","minEven","pctEven"]
    inRows = arcpy.da.InsertCursor(outVisitation,fields)
    for j in data:
        inRows.insertRow(j)
    del inRows
    
    # Set output
    arcpy.SetParameter(4,outVisitation)
    


except arcpy.ExecuteError: 
    # Get the tool error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    print(msgs)

except:
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    # Return python error messages for use in script tool or Python Window
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)

    # Print Python error messages for use in Python / Python Window
    print(pymsg + "\n")
    print(msgs)

finally:
    if debug == False and len(deleteme) > 0:
        # cleanup intermediate datasets
        if debug == True: arcpy.AddMessage("Removing intermediate datasets...")
        for i in deleteme:
            if debug == True: arcpy.AddMessage("Removing: " + str(i))
            arcpy.Delete_management(i)
        if debug == True: arcpy.AddMessage("Done")
        
        