# Script Name: Insert WMO Station Data
# Description: Inserts or updates the input feature class with the input data supplied
#              in the column specified, taking geometry from the supplied station feature class
# Created By:  David Martin
# Date:        May 2012

import arcpy

inputFC = arcpy.GetParameterAsText(0)
inputData = arcpy.GetParameter(1)
colName = arcpy.GetParameterAsText(2)
stationFC = arcpy.GetParameterAsText(3)

# Set up an array of months with dicts for start and end dates

months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
m_start = dict(Jan="2000-01-01",Feb="2000-02-01",Mar="2000-03-01",Apr="2000-04-01",May="2000-05-01",Jun="2000-06-01",Jul="2000-07-01",Aug="2000-08-01",Sep="2000-09-01",Oct="2000-10-01",Nov="2000-11-01",Dec="2000-12-01")
m_end = dict(Jan="2000-01-31",Feb="2000-02-29",Mar="2000-03-31",Apr="2000-04-30",May="2000-05-31",Jun="2000-06-30",Jul="2000-07-31",Aug="2000-08-31",Sep="2000-09-30",Oct="2000-10-31",Nov="2000-11-30",Dec="2000-12-31")

# Get the shape field of the stationFC
desc = arcpy.Describe(stationFC)
stnShapeFieldName = desc.ShapeFieldName

# And get the shape field of the inputFC
desc = arcpy.Describe(inputFC)
inShapeFieldName = desc.ShapeFieldName

# And a bunch of appropriately delimited fields
delimitedField = arcpy.AddFieldDelimiters(stationFC, "IndexNbr")
delimitedStation = arcpy.AddFieldDelimiters(inputFC, "WMOStationNumber")
delimitedMonth = arcpy.AddFieldDelimiters(inputFC, "Month")

featcur, f_row, updcur, upd_row = None,None,None,None

try:
   # Open search cursor on inputData
   tabcur = arcpy.SearchCursor(inputData)

   # Open search cursor on stationFC
   stationcur = arcpy.SearchCursor(stationFC)

   # Loop through the rows in the inputData
   for t_row in tabcur:
      # Get the station number
      stnNo = t_row.getValue("WMO_Station_Number")
      # Search the stationFC for the WMO Station Number
      stationcur = arcpy.SearchCursor(stationFC, delimitedField + " = " + str(stnNo))
      geom = None
      for s_row in stationcur:
         # grab the geometry of the station
         geom = s_row.getValue(stnShapeFieldName)
      # Loop through the months
      for month in months:
         # Check whether there's a row to update
         updcur = arcpy.UpdateCursor(inputFC, delimitedStation + " = " + str(stnNo) + " AND " + delimitedMonth + " = '" + month + "'")
         upd_row = updcur.next()
         if (upd_row != None):
            # arcpy.AddMessage("Setting " + colName + " for " + month + " to " + str(t_row.getValue(month)))
            upd_row.setValue(colName, t_row.getValue(month))
            updcur.updateRow(upd_row)
            del upd_row
            del updcur
         else:
            # Create a new feature
            featcur = arcpy.InsertCursor(inputFC)
            f_row = featcur.newRow()
            f_row.setValue(inShapeFieldName, geom)
            f_row.setValue("WMOStationNumber", stnNo)
            f_row.setValue("StationName", t_row.getValue("Station_Name"))
            f_row.setValue("Month", month)
            f_row.setValue("MonthStarts",m_start[month])
            f_row.setValue("MonthEnds",m_end[month])
            f_row.setValue("Period",t_row.getValue("Period"))
            f_row.setValue(colName, t_row.getValue(month))
            featcur.insertRow(f_row)
            del f_row
            del featcur
except:
   if not arcpy.GetMessages() == "":
      arcpy.AddMessage(arcpy.GetMessages(2))

#finally:
#   if f_row:
#      del f_row
#   if featcur:
#      del featcur
#   if upd_row:
#      del upd_row
#   if updcur:
#      del updcur