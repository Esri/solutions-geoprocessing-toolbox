#----------------------------------------------------------------------------------
# Copyright 2013 Esri
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
#----------------------------------------------------------------------------------
# CalcSIDCField.py
# Description: Sets the SIDC field from the Representation Rule name 
# Requirements: ArcGIS Desktop Standard
#----------------------------------------------------------------------------------

import os
import sys
import traceback
import arcpy
import MilitaryUtilities
import DictionaryConstants

### Params:
### 0 - inputFC
### 1 - sidc field
### 2 - echeclon field
### 3 - affiliation ("NOT_SET", "FRIENDLY", "HOSTILE", "NEUTRAL", "UNKNOWN")

try :

    # Get input feature class
    inputFC = arcpy.GetParameter(0)
    if (inputFC is "" or inputFC is None):
        # Assumes TestData folder in same directory as .py
        inputFC = os.path.join(os.path.dirname(__file__),  "TestData/Test_Data_No_Sidc.gdb/FriendlyOperations/FriendlyOperationsL")

    if not arcpy.Exists(inputFC) :
        msg = "Input Dataset does not exist: " + str(inputFC) + " - exiting"
        arcpy.AddError(msg)
        raise IOError(msg) 
    
    desc = arcpy.Describe(inputFC)

    # Get input feature class
    SIDCField = arcpy.GetParameterAsText(1)
    if (SIDCField == "" or SIDCField is None):
        SIDCField = "sidc"

    standard = arcpy.GetParameterAsText(2)
    
    symbolDictionary = MilitaryUtilities.getSymbolDictionaryStandard(standard)
    
    # Get input feature class
    EchelonField = arcpy.GetParameterAsText(3)
    if (EchelonField == "" or EchelonField is None):
        EchelonField = "echelon"

    # Used to infer the affiliation from the dataset name
    dataPath = desc.path
    datasetName = desc.name

    # Get affiliation, needed because SIDC affiliation cannot always be derived from feature attributes
    affiliation = arcpy.GetParameterAsText(4)
    if (not (affiliation == "")) and (not affiliation is None) and (not affiliation in DictionaryConstants.validAffiliations) :
        if (affiliation <> "NOT_SET") :
            msg = "ValidAffiliations are " + str(DictionaryConstants.validAffiliations)
            arcpy.AddWarning(msg)
            affiliation = ""

    if (affiliation == "") or (affiliation is None) or (affiliation == "NOT_SET") :
        affiliation = ""
        # If not set, then try to derive from the feature class name 
        # This will work with the default Military Features lpk/FGDB
        dataPathUpper = dataPath.upper()
        datasetNameUpper = datasetName.upper()
        if DictionaryConstants.FRIENDLY_AFFILIATION in dataPathUpper \
            or DictionaryConstants.FRIENDLY_AFFILIATION in datasetNameUpper :
            affiliation = DictionaryConstants.FRIENDLY_AFFILIATION
        elif DictionaryConstants.HOSTILE_AFFILIATION in dataPathUpper \
            or DictionaryConstants.HOSTILE_AFFILIATION in datasetNameUpper :
            affiliation = DictionaryConstants.HOSTILE_AFFILIATION
        elif DictionaryConstants.NEUTRAL_AFFILIATION in dataPathUpper \
            or DictionaryConstants.NEUTRAL_AFFILIATION in datasetNameUpper :
            affiliation = DictionaryConstants.NEUTRAL_AFFILIATION
        elif DictionaryConstants.UNKNOWN_AFFILIATION in dataPathUpper \
            or DictionaryConstants.UNKNOWN_AFFILIATION in datasetNameUpper :
            affiliation = DictionaryConstants.UNKNOWN_AFFILIATION
    
        if (affiliation is "") or (affiliation is None) :
            # default to Friendly, if still not set            
            arcpy.AddWarning("WARNING: could not determine affiliation, defaulting to " + \
                           DictionaryConstants.FRIENDLY_AFFILIATION)
            affiliation = DictionaryConstants.FRIENDLY_AFFILIATION

    ##Calculation Code

    #Get Symbol Field Name
    fieldNameList = []
    for field in desc.Fields:
        fieldNameList.append(field.name)

    updatefields = []

    if (SIDCField in fieldNameList) :
        updatefields.append(SIDCField)
    else :
        
        raise arcpy.ExecuteError()
        
    CODE_FIELD_NAME = "code"
    DESCRIPTION_FIELD_NAME = "description"
    fieldNameToDomainName = {}

    symbolNameFieldName = "symbolname"
    if ("ruleid" in fieldNameList):
        symbolNameFieldName = "ruleid"
    elif ("symbol_id" in fieldNameList):
        symbolNameFieldName = "Symbol_ID"
    elif ("symbolrule" in fieldNameList):
        symbolNameFieldName = "symbolrule"
    updatefields.append(symbolNameFieldName)

    if (EchelonField in fieldNameList):
        updatefields.append(EchelonField)

    for field in desc.Fields:
        if field.name in updatefields:
            # Get domain if any
            if (field.domain is not None and field.domain != ""):
                fieldNameToDomainName[field.name] = field.domain
                if arcpy.Exists("in_memory/" + field.domain):
                    arcpy.Delete_management("in_memory/" + field.domain)
                try:
                    #If path is feature class
                    arcpy.DomainToTable_management(desc.path, field.domain,
                                                   "in_memory/" + field.domain,
                                                   CODE_FIELD_NAME, DESCRIPTION_FIELD_NAME)
                except:
                    #If path is feature dataset
                    arcpy.DomainToTable_management(arcpy.Describe(desc.path).path, field.domain,
                                                   "in_memory/" + field.domain,
                                                   CODE_FIELD_NAME, DESCRIPTION_FIELD_NAME)
        
    with arcpy.da.UpdateCursor(inputFC, updatefields) as cursor:
        for row in cursor:
            #Lookup Symbol ID Value    
            SymbolIdCodeVal = ""
            echelonString = ""
            if (symbolNameFieldName in fieldNameToDomainName):
                domain = fieldNameToDomainName[symbolNameFieldName]
                whereClause = "%s = %s" % (CODE_FIELD_NAME, row[1])
                domainRows = arcpy.SearchCursor("in_memory/" + domain, whereClause)
                for domainRow in domainRows:
                    symbolname = domainRow.getValue(DESCRIPTION_FIELD_NAME)
                    # if (desc.shapeType == "Point" ) and (MilitaryUtilities.symbolDictionary.endsInAffilationString(symbolname)) :
                    # if (MilitaryUtilities.symbolDictionary.endsInAffilationString(symbolname)) :
                    # affiliationChar = symbolname[-1:]
                    #     symbolname = symbolname[:-2]       # Trim the F, H, U, N from the symbol name
                    #else :
                    #    affiliationChar = ''
            if (EchelonField in updatefields and row[2] is not None):
            ## TODO - this needs more testing (and moved to SymbolDictionary)
                echelonString = row[2]
                if (EchelonField in fieldNameToDomainName):
                    domain = fieldNameToDomainName[EchelonField]
                    whereClause = "%s = %s" % (CODE_FIELD_NAME, row[2])
                    domainRows = arcpy.SearchCursor("in_memory/" + domain, whereClause)
                    for domainRow in domainRows:
                        echelonString = domainRow.getValue(DESCRIPTION_FIELD_NAME)
                        echelonString = echelonString.upper()

            expectedGeometry = DictionaryConstants.getGeometryStringFromShapeType(desc.shapeType)
                        
# sidc = MilitaryUtilities.symbolDictionary.SymbolNametoSymbolIDExt(symbolname, echelonString, affiliation, expectedGeometry)
            sidc = symbolDictionary.SymbolNametoSymbolIDExt(symbolname, echelonString, affiliation, expectedGeometry)
            
# validSic = MilitaryUtilities.symbolDictionary.isValidSidc(sidc)
            validSic = symbolDictionary.isValidSidc(sidc)

            if not validSic :
                # this should not happen, but final check
                defaultSidc = DictionaryConstants.getDefaultSidcForShapeType(desc.shapeType)
                print "Invalid Sic Code: " + sidc + ", using default: " + defaultSidc
                sidc = defaultSidc

            #if len(affiliationChar) == 1 :
            #    row[0] = val[0] + affiliationChar + val[2:15]
            #    print val[0]
            #    print affiliationChar
            #    print val[2:14]
            #else :
            row[0] = sidc

            # update the feature
            cursor.updateRow(row)
            
    # Set output
    arcpy.SetParameter(5, inputFC)            

except arcpy.ExecuteError: 
    # Get the tool error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    print msgs

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
    print pymsg + "\n"
    print msgs

