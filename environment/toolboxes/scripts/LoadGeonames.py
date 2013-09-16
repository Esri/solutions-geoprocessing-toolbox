#!/usr/bin/env python
# Import ArcPy site-package and os modules
#
import arcpy 
import os
import sys, traceback
import time
from datetime import datetime
from datetime import date

lineCount = 0

## ======================================================
## Read in parameters
## ======================================================
featClass = arcpy.GetParameterAsText(0)
geonameFilePath = arcpy.GetParameterAsText(1)
countryCodeTable = arcpy.GetParameterAsText(2)
admin1CodeTable = arcpy.GetParameterAsText(3)
featureCodeTable = arcpy.GetParameterAsText(4)
desc= arcpy.Describe(featClass)
fieldNameList = [field.name for field in desc.Fields] 
    
## ======================================================
## Read geoname file and insert feature
## ======================================================

try:
    # Defines how many features have to be inserted before it will
    # report status
    reportNum = 10000
    
    row, rows, pntObj = None, None, None

    rowCC, rowsCC = None, None
    
    rowADM1, rowsADM1 = None, None
    
    rowFeatCode, rowsFeatCode = None, None
    
    pntObj = arcpy.Point()
    
    # ======================================================
    # Create CountryCode/CountryName dictionary
    # ======================================================
    arcpy.AddMessage("- Reading CountryCode table " + countryCodeTable + "...")

    # Create dictionary
    countryCodeDict = {}
    
    # Create search cursor
    rowsCC = arcpy.SearchCursor(countryCodeTable)

    # Loop through cursor and extract values into dictionary
    for rowCC in rowsCC:
        countryCodeDict[rowCC.Code] = rowCC.Name

    # ======================================================
    # Create Primary Administrative Code/Administrative Name dictionary and
    # Primary Administrative Code/Administrative Class dictionary
    # ======================================================
    arcpy.AddMessage("- Reading Primary Administrative Code table " + admin1CodeTable + "...")

    # Create dictionaries
    admin1CodeDict = {}
    admin1ClassDict = {}
    
    # Create search cursor
    rowsADM1 = arcpy.SearchCursor(admin1CodeTable)

    # Loop through cursor and extract values into dictionary
    for rowADM1 in rowsADM1:
        admin1CodeDict[rowADM1.Code] = rowADM1.Name
        admin1ClassDict[rowADM1.Code] = rowADM1.AdminDivisionClass
        
    # ======================================================
    # Create Feature Code/Feature Name dictionary
    # ======================================================
    arcpy.AddMessage("- Reading Feature Code table " + featureCodeTable + "...")

    # Create dictionary
    featCodeDict = {}
    
    # Create search cursor
    rowsFeatCode = arcpy.SearchCursor(featureCodeTable)

    # Loop through cursor and extract values into dictionary
    for rowFeatCode in rowsFeatCode:
        featCodeDict[rowFeatCode.Code] = rowFeatCode.Name
        
    # ======================================================
    # Loop through geonames file and insert features
    # ======================================================

    # Get list of fields in feature class   
    fieldListFC = arcpy.ListFields(featClass)
    
    # Open geoname file
    arcpy.AddMessage("- Opening geoname file " + geonameFilePath + "...")

    fileGeoname = open(geonameFilePath, "r")

    # Create insert cursor
    rows = arcpy.InsertCursor(featClass)
    
    arcpy.AddMessage("- Creating features (report progress every " + str(reportNum) + " features)...")

    for lineGeoname in fileGeoname:
        lineCount = lineCount + 1

        # Reset variables
        lat = ''
        long = ''
        ufi = ''
        uni = ''                       
        adm1 = ''
        countryCode1 = ''            
        placeName = ''
        featDSGCode = ''
        adm1NameAll = ''
        adm1Name = ''
        adm1ClassAll = ''
        adm1Class = ''
        mgrs = ''
        userValue = ''
        
        # Geoname file is Tab delimited so split line by Tab
        fileFieldValueList = lineGeoname.split("\t")
        
        # Create list of field names from first line of file
        if lineCount == 1:
            
            fileFieldList = fileFieldValueList
            
        else:
            
            # Create new row
            row = rows.newRow()
    
            # Populate feature class fields from text file
            fieldIndex = 0
            for fieldValue in fileFieldValueList:
                
                # Remove any trailing newline character from field name
                #   and field value
                fieldName = fileFieldList[fieldIndex].rstrip('\n')
                fieldValue = fieldValue.rstrip('\n')
                
                if fieldValue <> '':
                    
                    # Format date value
                    if fieldName.upper() == "MODIFY_DATE":
                        fieldValue = fieldValue + " 00:00:00 AM"
                    
                    if fieldName.upper() == "CC1":
                        country1List = fieldValue.split(",")
                        countryCode1 = country1List[0]
                        row.setValue("COUNTRYCODE1", countryCode1)
                        
                        # Populate country name field
                        countryName = countryCodeDict.get(countryCode1)
                        
                        if countryName is None:
                            row.setNull("COUNTRYNAME1")
                        else:
                            row.setValue("COUNTRYNAME1", countryName)
                        
                    # Extract Latitude and Longitude values to create
                    # point geometry
                    if fieldName.upper() == "LAT":
                        lat = fieldValue
                        
                    if fieldName.upper() == "LONG":
                        long = fieldValue
                    
                    if fieldName.upper() == "UFI":
                        ufi = fieldValue

                    if fieldName.upper() == "UNI":
                        uni = fieldValue                       

                    if fieldName.upper() == "ADM1":
                        adm1 = fieldValue
                    
                    if fieldName.upper() == "FULL_NAME_ND_RO":
                        placeName = fieldValue
                    
                    if fieldName.upper() == "DSG":
                        featDSGCode = fieldValue
                    
                    if fieldName.upper() == "MGRS":
                        mgrs = fieldValue
                            
                    
                        
                    # Populate geodatabase field with text file value 
                    try:
                        
                        if fieldName in fieldNameList:
                          
                            row.setValue(fieldName, fieldValue)
                    except:
                        
                        arcpy.AddWarning("exception setting field name: " + fieldName)
                     
                else:
                    row.setNull(fieldName)
                    
                fieldIndex = fieldIndex + 1
            
            # Set CountryCode/First-order Administrative Class field value
            if countryCode1 <> '' and adm1 <> '':
                row.setValue("ADM1CODE", countryCode1 + adm1)
                
                # Populate primary admin field value
                adm1NameAll = admin1CodeDict.get(countryCode1 + adm1)
                
                if adm1NameAll is None:
                    row.setNull("ADM1NAMEALL")
                else:
                    row.setValue("ADM1NAMEALL", adm1NameAll)
                    
                    ## Populate ADM1NAME field with first name in list
                    #
                    # Extract first element:
                    # some admin name have multiple "versions" for
                    # example BE11 is
                    # "Brussels-Capital Region [conventional] /
                    # Brussels Hoofdstedelijk [Dutch] /
                    # Bruxelles-Capitale [French]"
                    #
                    # Extract first value minus "/", "[", "]" and
                    # contents within brackets
                    adm1Name = adm1NameAll.split("/")[0].split("[")[0].strip()
                    row.setValue("ADM1NAME", adm1Name)
                    
                    userValue = "Principal Admin Division: " + adm1Name
                    
                    ## Populate Admin Division Class field (ADM1CLASS)
                    adm1ClassAll = admin1ClassDict.get(countryCode1 + adm1)
                    
                    if adm1ClassAll is None:
                        row.setNull("ADM1CLASSALL")
                        row.setNull("ADM1CLASS")
                    else:
                        row.setValue("ADM1CLASSALL", adm1ClassAll)
                        
                        # 'Assemble' the Admin1 Class value
                        i = adm1ClassAll.find("(")
                        if i > -1:
                            # Extract characters before "("
                            adm1Class = adm1ClassAll[:i].strip()
                            # Extract characters after ")"
                            adm1Type =  adm1ClassAll[i:].strip()
                        else:
                            adm1Class = adm1ClassAll
                            adm1Type = ''
                        
                        adm1Class = adm1Class.split("/")[0].split("[")[0].strip()
                        adm1Class = adm1Class + " " + adm1Type
                        # Remove trailing space that exists if adm1Type does
                        # not have a value
                        adm1Class = adm1Class.strip()
                        
                        row.setValue("ADM1CLASS", adm1Class)
                        
                        userValue = userValue + " [" + adm1Class + "]"
                        
                        row.setValue("USER_FLD", userValue)
                        
            # Set Feature Designation Name field value
            if featDSGCode <> '':
                
                featDSGName = featCodeDict.get(featDSGCode)
                
                if featDSGName is None:
                    row.setNull("DSGNAME")
                else:
                    row.setValue("DSGNAME", featDSGName)
            

            # Populate Place name field using the reading order non-diatrictic
            row.setValue("PLACENAME", placeName)
            
            # Set lat/long values on point object
            pntObj.Y = lat
            pntObj.X = long
            
            # Populate geometry
            row.Shape = pntObj
            
            # Insert feature
            try:
                rows.insertRow(row)
            except:
                arcpy.AddWarning("Error inserting row: " + str(lineCount))
            # Print progress
            if lineCount % reportNum == 0:
                arcpy.AddMessage("\tCreating feature number: " + str(lineCount))
        
    # Close met file 
    fileGeoname.close()
    
    # Set Output parameter (required so that script 
    # tool output can be connected to other model tools)
    arcpy.SetParameter(5, featClass)
    arcpy.AddMessage("Completed, " + str(lineCount) + " records completed")
    
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
    
finally:
    # Regardless of whether the script succeeds or not, delete 
    #  the row and cursor
    
    if row:
        del row
    if rows:
        del rows
    if pntObj:
        del pntObj

    # Close met file
    if fileGeoname:
        fileGeoname.close()
