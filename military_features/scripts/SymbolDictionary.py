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
# SymbolDictionary.py
# Description: .dat file table lookup routines (ex. SIDC <-> Name) 
#----------------------------------------------------------------------------------

import sqlite3
import os
import DictionaryConstants
import re
import arcpy

class SymbolDictionary(object):
    """ 
    Lookup methods & helpers for mappings between SIDC, Name, GeometryType, etc.
    Generally just does a straight lookup of the dictionary data file with
    some attempts to correct common lookup errors (ex. not including "H" when
    looking up a name for a hostile unit. 
    TRICKY: the methods that operate on Representation Rule IDs, e.g. symbolIdToRuleId, 
            must have first have called initializeRulesByMilitaryFeatures(validRepresenationLayer) 
    """

    def __init__(self, dictionaryPathAndFile) :
        self.dictionaryFile = dictionaryPathAndFile

        self.RuleID2Name = {}
        self.Name2RuleID = {}

        # Echelons map: echelon name (upper case) -> SIC positions 11 and 12
        self.echelonToSIC1112 = dict([ \
                ('TEAM/CREW', '-A'), \
                ('SQUAD', '-B'), \
                ('SECTION', '-C'), \
                ('PLATOON/DETACHMENT', '-D'), \
                ('COMPANY/BATTERY/TROOP', '-E'), \
                ('BATTALION/SQUADRON', '-F'), \
                ('REGIMENT/GROUP', '-G'), \
                ('BRIGADE', '-H'), \
                ('DIVISION', '-I'), \
                ('CORPS/MEF', '-J'), \
                ('ARMY', '-K'), \
                ('ARMY GROUP/FRONT', '-L'), \
                ('REGION', '-M'), \
                ('COMMAND', '-N') \
                ])

        # Symbol/Rule ID Name to SIDC mapping 
        self.nameToSIC = dict([ \
        ###########################################
        ## TODO - If you have rule names that do not match the standard Military Features convention
        ## you must add them here(in UpperCase), or otherwise set in this dictionary. Example shown:
        ###########################################
                ("STRYKER BATTALION",            "SFGPUCII---F---"), \
                ("STRYKER CAVALRY TROOP",        "SFGPUCRRL--E---"), \
                ("FIELD ARTILLERY BATTALION",    "SFGPUCF----F---"), \
                ("STRYKER HEADQUARTERS COMPANY", "SFGPUH-----E---"), \
                ("BRIGADE SUPPORT BATTALION",    "SFGPU------F---"), \
                ("INFANTRY PLATOON F", "SFGPUCI----D---")
                ])

        if (os.path.isfile(self.dictionaryFile)) :
            print "SymbolDictionary Initialized"
            self.initalized = True
        else :
            arcpy.AddError("SymbolDictionary Initialization: FAILED")
            self.initalized = False

            #TODO: determine if this is a fatal error, for now assume it is
            msg = "Exiting: Dictionary File does not exist: " + self.dictionaryFile
            arcpy.AddError(msg)
            raise IOError(msg) 

        print "Using dictionary file: " + self.dictionaryFile
        
    def getSymbologyStandard(self) :
        if (self.dictionaryFile is None) or (self.dictionaryFile == "") : 
            print "WARNING: standard is null, using default"
            return "NOT SET"
             
        if (self.dictionaryFile.upper().find("APP6") >= 0) :
            return "APP6"
        else :
            return "2525"                    
    
    # Helper to RegEx test/validate a SIDC for basic correctness 
    # IMPORTANT: does not guarantee correctness
    def isValidSidc(self, sidc) :
        validSicRegex = "^[SGWIOE][PUAFNSHGWMDLJKO\-][PAGSUFXTMOEVLIRNZC\-][APCDXF\-][A-Z0-9\-]{6}[A-Z\-]{2}[A-Z0-9\-]{2}[AECGNSX\-]$"
        matching = bool(re.match(validSicRegex, sidc))
        return matching

    def getRuleID2NameDictionary(self) :
        return self.RuleID2Name

    def getName2RuleIDDictionary(self) :
        return self.Name2RuleID

    def getDictionaryPath(self) :
        return self.dictionaryFile

    def getAffiliationChar(self, sic) :
        ch = sic.upper()[1]
        if (ch == 'F') or (ch == 'H') or (ch == 'U') or (ch == 'N') :
            return ch;
        elif (ch == 'M') or (ch == 'A') or (ch == 'D') or (ch == 'J') or (ch == 'K') :
            return 'F'
        elif (ch == 'S') :
            return 'H'
        elif (ch == 'L') :
            return 'N'
        elif (ch == 'P') or (ch == 'G') or (ch == 'W') or (ch == '-') :
            return 'U'
        else :
            print "Unrecognized affiliation"
            return 'U'

    def getMaskedSymbolIdFirst10(self, sic) : 
        if len(sic) < 10 :
            upperSic = DictionaryConstants.DEFAULT_POINT_SIDC 
        else :
            upperSic = sic.upper()
        maskedSic = upperSic[0] + self.getAffiliationChar(upperSic) \
            + upperSic[2] + 'P' + upperSic[4:10]
        return maskedSic[0:10]

    def getSymbolAttribute(self, symbolId, attribute) : 

        sqliteConn = None
        sqliteCursor = None
        symboldictionary = self.getDictionaryPath() 
        sqliteConn = sqlite3.connect(symboldictionary)
        sqliteCursor = sqliteConn.cursor()

        lookupSic = self.getMaskedSymbolIdFirst10(symbolId)  
        lookupSic = lookupSic.upper()                  

        query = "select " + attribute + " from SymbolInfo where (ID = ?)"
        sqliteCursor.execute(query, (lookupSic,))
        sqliteRow = sqliteCursor.fetchone()

        # some only have 'F' version
        if (sqliteRow == None) :
            lookupSic = lookupSic[0] + 'F' + lookupSic[2] + 'P' + lookupSic[4:10]
            sqliteCursor.execute(query, (lookupSic,))
            sqliteRow = sqliteCursor.fetchone()            

        if (sqliteRow == None) :
            print "WARNING: " + symbolId + ":" + attribute + " NOT FOUND"
            val = "None"
        else :
            val = sqliteRow[0]

        # print symbolId, attribute, val
        return val

    def symbolIdToGeometryType(self, symbolId) :

        sqliteConn = None
        sqliteCursor = None
        symboldictionary = self.getDictionaryPath() 
        sqliteConn = sqlite3.connect(symboldictionary)
        sqliteCursor = sqliteConn.cursor()

        lookupSic = self.getMaskedSymbolIdFirst10(symbolId)
        lookupSic = lookupSic.upper()

        query = "select GeometryType from SymbolInfo where (ID = ?)"
        sqliteCursor.execute(query, (lookupSic,))
        sqliteRow = sqliteCursor.fetchone()
        
        # some only have 'F' version
        if (sqliteRow == None) :
            lookupSic = lookupSic[0] + 'F' + lookupSic[2] + 'P' + lookupSic[4:10]
            sqliteCursor.execute(query, (lookupSic,))
            sqliteRow = sqliteCursor.fetchone()                   
        
        if (sqliteRow == None) :
            geoType = "None"
        else :
            geoChar = sqliteRow[0]

            if (geoChar == 'P') :
                geoType = DictionaryConstants.POINT_STRING
            elif (geoChar == 'L') :
                geoType = DictionaryConstants.LINE_STRING
            elif (geoChar == 'A') :
                geoType = DictionaryConstants.AREA_STRING

        # print symbolId, geoType
        return geoType

    def symbolIdToGeometryConversionType(self, symbolId) : 

        sqliteConn = None
        sqliteCursor = None
        symboldictionary = self.getDictionaryPath() 
        sqliteConn = sqlite3.connect(symboldictionary)
        sqliteCursor = sqliteConn.cursor()

        lookupSic = self.getMaskedSymbolIdFirst10(symbolId)
        significant8Chars = lookupSic[2:10]
        significant8Chars = significant8Chars.upper()

        query = "select GCT from LnAExceptions where (Significant8Chars = ?)"
        sqliteCursor.execute(query, (significant8Chars,))
        sqliteRow = sqliteCursor.fetchone() 
            
        if (sqliteRow == None) :            
            geoType = self.symbolIdToGeometryType(symbolId)
            if (geoType == DictionaryConstants.POINT_STRING) : 
                conversionType = DictionaryConstants.GCT_POINT
            elif (geoType == DictionaryConstants.LINE_STRING) : 
                conversionType = DictionaryConstants.GCT_POLYLINE                                
            elif (geoType == DictionaryConstants.AREA_STRING) :
                conversionType = DictionaryConstants.GCT_POLYGON
            else :
                conversionType = DictionaryConstants.GCT_INDETERMINATE
        else :
            conversionType = sqliteRow[0]

        return conversionType
    
    def symbolIdToName(self, symbolId) :
        symbolName = self.getSymbolAttribute(symbolId, "Name")
        return symbolName

    def symbolIdToRuleId(self, symbolId) : 

        try :

            if len(self.RuleID2Name) == 0 :
                print "Rule IDs not initialized"
                return -1, ""

            symbolName = self.symbolIdToName(symbolId)

            if (symbolName is None) or (symbolName == "") :
                print "Symbol Name not found for SIDC: " + symbolId  
                return -1, ""

            if (self.endsInAffilationString(symbolName)) : 
                symbolName = symbolName[0:-2]

            if (self.endsInCircular(symbolName)) : 
                symbolName = symbolName[0:-9]
            elif (self.endsInRectangular(symbolName)) : 
                symbolName = symbolName[0:-12]
            elif (self.endsInIrregular(symbolName)) : 
                symbolName = symbolName[0:-10]            

            if (self.Name2RuleID.has_key(symbolName)) :
                ruleId = self.Name2RuleID[symbolName]
            else :
                
                # arcpy.AddWarning("Could not find RuleID for Symbol Name: " + symbolName)

                # WORKAROUND: we need to correct some names that don't match between Rules Names and Symbol Names
                correctedSymbolName = symbolName
                if self.endsInSafe(correctedSymbolName) :
                    correctedSymbolName = correctedSymbolName[0:-7]
                elif self.startsWithTaskScreen(correctedSymbolName) :
                    correctedSymbolName = correctedSymbolName.replace('Task - Screen', 'Screen')

                if (self.Name2RuleID.has_key(correctedSymbolName)) :
                    ruleId = self.Name2RuleID[correctedSymbolName]
                else :
                    arcpy.AddWarning("Could not find RuleID for Symbol Name: " + correctedSymbolName)
                    ruleId = -1

        except :
            ruleId = -1
            arcpy.AddWarning("Unexpected Exception in symbolIdToRuleId() - using RuleId: " + str(ruleId))

        return ruleId, symbolName

    def endsInAffilationString(self, str) : 
        endsInRegex = ".* [FHNU]$"
        matching = bool(re.match(endsInRegex, str.upper()))
        return matching

    def endsInLeft(self, str) : 
        endsInRegex = ".*LEFT$"
        matching = bool(re.match(endsInRegex, str.upper()))
        return matching

    def endsInRight(self, str) : 
        endsInRegex = ".*RIGHT$"
        matching = bool(re.match(endsInRegex, str.upper()))
        return matching

    def endsInSafe(self, str) : 
        endsInRegex = ".*\(SAFE\)$"
        matching = bool(re.match(endsInRegex, str.upper()))
        return matching

    def endsInPAA(self, str) : 
        endsInRegex = ".*\(PAA\)$"
        matching = bool(re.match(endsInRegex, str.upper()))
        return matching

    def endsInCircular(self, str) : 
        endsInRegex = ".*CIRCULAR$"
        matching = bool(re.match(endsInRegex, str.upper()))
        return matching

    def endsInRectangular(self, str) : 
        endsInRegex = ".*RECTANGULAR$"
        matching = bool(re.match(endsInRegex, str.upper()))
        return matching

    def endsInIrregular(self, str) : 
        endsInRegex = ".*IRREGULAR$"
        matching = bool(re.match(endsInRegex, str.upper()))
        return matching

    def startsWithTaskScreen(self, str) : 
        startsWithRegex = "^(TASK - SCREEN).*"
        matching = bool(re.match(startsWithRegex, str.upper()))
        return matching
    
    def SymbolNametoSymbolID(self, symbolName) :
        # Lookup when looking up the Dictionary Name exactly as it appears in the Dictionary 
        return self.SymbolNametoSymbolIDExt(symbolName, "", "", "")

    def SymbolNametoSymbolIDExt(self, symbolName, echelonString, affiliation, expectedGeometry) :

        # Attempts to handle the many name cases that show up in Military Features
        # A straight Dictionary Name to SIDC case should always work, but the names
        # don't always show up in that form, use SymbolNametoSymbolID for simple case
         
        foundSIC = False
        add2Map  = False
        symbolNameUpper = symbolName.upper()
        
        # Tricky: the Append Features Tools adds to the base name with "~" so remove all after "~"
        # see SymbolCreator.cs/GetRuleNameFromSidc for separator character/format
        symbolNameUpper = symbolNameUpper.split("~")[0].strip()

        # print ("Using Symbol " + sidc)
        if (symbolNameUpper in self.nameToSIC):
            # Skip the SQL query, because we have already found this one (or it is hardcoded)
            sidc = self.nameToSIC[symbolNameUpper]
            foundSIC = True
        else:
            sqliteConn = None
            sqliteCursor = None
            symboldictionary = self.getDictionaryPath()
            sqliteConn = sqlite3.connect(symboldictionary)
            sqliteCursor = sqliteConn.cursor()
            # SQL query (or two) to find SIC
            sqliteCursor.execute("SELECT SymbolId FROM SymbolInfo WHERE UPPER(Name) = ?", (symbolNameUpper,))
            sqliteRow = sqliteCursor.fetchone()

            if (sqliteRow == None):
                # if it is not found with the supplied name, we need to try a few more cases:
                # remove 1) affilition 2) "Left" / "Right" 
                if self.endsInAffilationString(symbolNameUpper) :
                    symbolNameUpper = symbolNameUpper[0:-2] 
                elif self.endsInLeft(symbolNameUpper) : 
                    symbolNameUpper = symbolNameUpper[0:-5]
                elif self.endsInRight(symbolNameUpper) : 
                    symbolNameUpper = symbolNameUpper[0:-6]

                if (symbolNameUpper in self.nameToSIC):
                    # Check again with modfied name
                    sidc = self.nameToSIC[symbolNameUpper]
                    foundSIC = True
                else :
                    queryval = symbolNameUpper + "%"
                    sqliteCursor.execute("SELECT SymbolId FROM SymbolInfo WHERE UPPER(Name) like ?", (queryval,))
                    sqliteRow = sqliteCursor.fetchone()

                    # Yet another failing case "some have '-' some don't, ex. "Task - Screen" <-> "Task Screen"
                    if (sqliteRow == None):
                        queryval = '%' + symbolNameUpper + '%'
                        sqliteCursor.execute("SELECT SymbolId FROM SymbolInfo WHERE (UPPER(Name) like ?)", (queryval,))
                        sqliteRow = sqliteCursor.fetchone()

            if (sqliteRow != None):
                foundSIC = True
                sidc = sqliteRow[0].replace("*", "-")
                add2Map = True

        if (foundSIC) and self.isValidSidc(sidc):
            # If it is now a valid SIDC, replace chars 11 and 12 (in Python that's 10 and 11) with the echelon code
            if (echelonString in self.echelonToSIC1112):
                sidc = sidc[0:10] + self.echelonToSIC1112[echelonString] + sidc[12:]

            # Then check affiliation char (the correct one is not always returned)
            if not ((affiliation is None) or (affiliation is "")) :  
                affiliationChar = sidc[1]
                expectedAffiliationChar = DictionaryConstants.affiliationToAffiliationChar[affiliation]
    
                if affiliationChar != expectedAffiliationChar :
                    print "Unexpected Affiliation Char: " + affiliationChar + " != " + expectedAffiliationChar
                    sidc = sidc[0] + expectedAffiliationChar + sidc[2:]

            if add2Map : 
                # add the query results to the map (if valid)
                self.nameToSIC[symbolNameUpper] = sidc            
                print "Adding to Map: [" + symbolNameUpper + ", " + sidc + "]"
        else:
            defaultSidc = DictionaryConstants.getDefaultSidcForGeometryString(expectedGeometry)
            sidc = defaultSidc
            warningMsg = "Warning: Could not map " + symbolNameUpper + " to valid SIDC - returning default: " + sidc
            arcpy.AddWarning(warningMsg)

        return sidc            

    def initializeRulesByMilitaryFeatures(self, featureClass) :
        # Military Feature use several different possible fields to store this Rule ID        
        desc = arcpy.Describe(featureClass)
        CODE_FIELD_NAME = "code"
        DESCRIPTION_FIELD_NAME = "description"
        ruleFieldName = None
        ruleDomainName = None
        for field in desc.Fields:
            if (field.name in DictionaryConstants.RuleFieldsList):
                if (field.domain is not None and field.domain != ""):
                    # Note Bene: only works with FGDBs (assumes MilFeature only stored in these)
                    dataPath = desc.path
                    gdbPath = dataPath.split(".gdb")[0]
                    gdbPath += ".gdb"
                    ruleFieldName = field.name
                    ruleDomainName = field.domain
                    arcpy.DomainToTable_management(gdbPath, field.domain, "in_memory/" + ruleDomainName, CODE_FIELD_NAME, DESCRIPTION_FIELD_NAME)
                    break

        # map both ways for performance/simplicty of use
        ruleID2Name = self.getRuleID2NameDictionary()
        name2RuleID = self.getName2RuleIDDictionary()

        symbolCount = 0
        if (ruleFieldName is None) or (ruleDomainName is None) :
            arcpy.AddError("Layer RuleId not found, can't continue")
        else :
            print "Symbol RuleId found & exporting: " + ruleFieldName
            domainRows = arcpy.SearchCursor("in_memory/" + ruleDomainName)
            for domainRow in domainRows:
                ruleid = domainRow.getValue(CODE_FIELD_NAME)
                symbolname = domainRow.getValue(DESCRIPTION_FIELD_NAME)

                if self.endsInPAA(symbolname) : 
                    symbolname = symbolname[0:-6]

                symbolCount = symbolCount + 1
                print str(ruleid) + " --> " + symbolname
                ruleID2Name[ruleid] = symbolname
                name2RuleID[symbolname] = ruleid

        if symbolCount == 0 :
            arcpy.AddError("No Layer RepRules found, can't continue")
            ruleFieldName = None
        elif symbolCount < 50 :
            arcpy.AddWarning("Only " + str(symbolCount) + " RepRules found, may not work as expected")

        return ruleFieldName




