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
# WriteFeatureFromMessage.py
# Description: Converts XML file to Military Feature Class
# Limitations: The Military Feature Representation Rule can not be set if it does not 
#              already exist
#----------------------------------------------------------------------------------

import arcpy
import MessageIterator
import MilitaryUtilities
import GeometryConverter
import DictionaryConstants
import os.path
import traceback

### Params:
### 0 - inputXMLFileName
### 1 - outputFeatureClass
### 2 - symbology standard (2525, APP6)
### 3 - MessageType field

def writeFeaturesFromMessageFile() :

    foundEmptyRuleId = False  # used to detect if we can not set a RuleID for any rows

    # Get the input message file
    inputFileName = arcpy.GetParameterAsText(0)
    if (inputFileName == "") or (inputFileName is None):
        inputFileName = os.path.join(MilitaryUtilities.dataPath, r"/messages/Mil2525CMessages.xml")
                
    if not os.path.isfile(inputFileName) :
        arcpy.AddError("Bad Input File: " + inputFileName)
        return

    inputFile=open(inputFileName, "r")
    if (inputFile is None) : 
        arcpy.AddError("Input file can't be opened, exiting")
        return
        
    # Get the output feature class
    outputFC = arcpy.GetParameter(1)
    if (outputFC == "") or (outputFC is None):
        outputFC = os.path.join(MilitaryUtilities.geoDatabasePath, r"/test_outputs.gdb/FriendlyOperations/FriendlyUnits")
        
    desc = arcpy.Describe(outputFC)
    if desc == None :
        arcpy.AddError("Can't open Output Dataset: " + str(outputFC)) 
        return

    shapeType = desc.shapeType;

    # Get standard
    standard = arcpy.GetParameterAsText(2)
        
    # Message Type Field
    messageTypeField = arcpy.GetParameterAsText(3)            

    arcpy.AddMessage("Running with Parameters:")
    arcpy.AddMessage("0 - input XML File: " + str(inputFileName))
    arcpy.AddMessage("1 - output FC: " + str(outputFC))
    arcpy.AddMessage("2 - symbology standard: " + str(standard))        
    arcpy.AddMessage("3 - MessageTypeField: " + messageTypeField)
        
    if not ((messageTypeField == "") or (messageTypeField is None)) :
        if desc.Fields.contains(field) :
            MilitaryUtilities.MessageTypeField = messageTypeField
        else :
            arcpy.AddWarning("MessageTypeField does not exist in output: " + MessageTypeField + " , using default")

    print "Exporting message objects from: " + str(inputFileName)
    print "To Feature Class: " + str(outputFC)
    print "That match shape type: " + shapeType

    # initialize the standard
    MilitaryUtilities.getGeometryConverterStandard(standard)
        
    ruleFieldName = MilitaryUtilities.symbolDictionary.initializeRulesByMilitaryFeatures(outputFC) 

    if (ruleFieldName == "") or (ruleFieldName is None) :
        arcpy.AddError("RuleFieldName not found, exiting")
        return

    # Projected or geographic?
    xname = "lon"
    yname = "lat"
    isProjected = desc.spatialReference.type == "Projected"
    if (isProjected):
        xname = "x"
        yname = "y"
    outputWkid = desc.spatialReference.factoryCode

    ################Begin Export ##########################
    
    featureFields = desc.fields

    # Iterate through the messages and check the shape
    WRITE_OUTPUT = True # debug switch when output not needed
    newRow = None
    newRows = None

    try : 

        if WRITE_OUTPUT : 
            newRows = arcpy.InsertCursor(outputFC)
        messageCount = 0

        # for each message in the message file, get its attributes and copy to the output FeatureClass
        for sic, controlPoints, attributes in MessageIterator.MessageIterator(inputFileName) :
            print sic, controlPoints, attributes

            geoType = MilitaryUtilities.geoConverter.expectedGeometryType(sic)
            if not DictionaryConstants.isCorrectShapeTypeForFeature(geoType, shapeType) : 
                skipMsg = "Skipping SIC: " + sic + " - does not match feature type" + shapeType
                arcpy.AddMessage(skipMsg)
                continue

            # Used for those SICs that map to 2 lines (ex. Task Screen/Guard/Cover)
            repeatForPairFeatures = True
            repeatCount = 0

            while repeatForPairFeatures :

                outputPointList, conversionNotes = MilitaryUtilities.geoConverter.controlPointsToGeometry(sic, controlPoints, attributes)
                if outputPointList == None :
                    msg = "Failed to Convert Points from Military to MilFeature format for SIDC: " + sic
                    arcpy.AddError(msg)
                    arcpy.AddError("Conversion Notes: " + conversionNotes)
                    repeatForPairFeatures = False
                    continue

                inputWkid = 0
                if attributes.has_key(DictionaryConstants.Tag_Wkid) :
                    inputWkid = int(attributes[DictionaryConstants.Tag_Wkid])

                if outputWkid != inputWkid :
                    msg = "ERROR: Input Message and Output Feature WKIDs do not match (InsertFeature will fail)"
                    arcpy.AddError(msg)
                    msg = "Output WKID = " + str(outputWkid) + " , Input WKID = " + str(inputWkid)
                    arcpy.AddError(msg)

                ruleId, symbolName = MilitaryUtilities.symbolDictionary.symbolIdToRuleId(sic)

                if ruleId < 0 :
                    foundEmptyRuleId = True
                    # arcpy.AddWarning("WARNING: Could not map ruleId to SIDC: " + sic)

                # For those SIC that map to 2 lines (ex. Task Screen/Guard/Cover)
                # will need to clone/repeat the message here for Left/Right Upper/Lower pair
                repeatForPairFeatures = False 
                geoConversion = MilitaryUtilities.symbolDictionary.symbolIdToGeometryConversionType(sic)
                if (geoConversion == DictionaryConstants.GCT_TWOLINE) or \
                    (geoConversion == DictionaryConstants.GCT_TWOLINE3OR4PT) :
                    if repeatCount > 0 : 
                        repeatForPairFeatures = False # Only do once
                        ## TODO: find better way to set rule Id for 2nd line (Left/Right) version
                        # This is quite kludgy, and relies on the 2nd ruleid code being the 1st + 1
                        # and this may not always be the case
                        ruleId = ruleId + 1
                    else : 
                        repeatForPairFeatures = True 
                        attributes[DictionaryConstants.Tag_TwoLinesNeeded] = "True"
                        # don't let id get repeated, so append "_2"
                        if attributes.has_key(DictionaryConstants.Tag_Id) : 
                            attributes[DictionaryConstants.Tag_Id] = attributes[DictionaryConstants.Tag_Id] + "_2"
                repeatCount = repeatCount + 1

                arcpy.AddMessage("Adding feature #" + str(messageCount) + " with SIDC: " + sic)
                if WRITE_OUTPUT : 
                    try : 
                        shape = MilitaryUtilities.pointsToArcPyGeometry(outputPointList, shapeType)
                        newRow = newRows.newRow()
                        newRow.setValue(desc.shapeFieldName, shape)
                        newRow.setValue(ruleFieldName, ruleId)
                        
                        # both "sic" and "sidc" used
                        try : 
                            newRow.setValue("sic", sic)
                        except :
                            try :                             
                                newRow.setValue("sidc", sic)
                            except : 
                                arcpy.AddWarning("Failed to set SIDC field in output")
                            
                        # add any extra fields
                        for field in featureFields :  
                            if not (field.name in DictionaryConstants.MILFEATURES_FIELD_EXCLUDE_LIST) :
                                lowerFieldName = field.name.lower()
                                # we don't the case of the attribute so have to search
                                for key in attributes.keys() :                                     
                                    lowerKey = key.lower() 
                                    if (lowerKey == lowerFieldName) :
                                        try : 
                                            newRow.setValue(field.name, attributes[key])
                                        except : 
                                            print "Could not add: Field: " + field.name + ", Value: " + str(attributes[key])

                        newRows.insertRow(newRow) 
                        arcpy.AddMessage("Message successfully added: " + str(messageCount))
                    except : 
                        arcpy.AddError("ERROR: Exception while adding new feature (does Spatial Ref match?)")
                        tb = traceback.format_exc()
                        print tb
                else :
                    print "WRITING OUTPUT:"
                    print "SIC: " + sic + ", Name: " + symbolName                
                    print "Adding geometry to feature, with points: "
                    for point in outputPointList : 
                        x = point.split(',')[0]
                        y = point.split(',')[1]
                        print "(", x, ",", y, ")"                                     
                
            messageCount += 1
            
        if messageCount == 0 :
            arcpy.AddWarning("No Messages Found in Input")

        if foundEmptyRuleId :
            arcpy.AddWarning("IMPORTANT: Some rows do not have Symbol RuleId set - you may need to run CalcRepRuleField tool.")            
           
    except :
        tb = traceback.format_exc()
        arcpy.AddError("Exception:")
        arcpy.AddError(tb)        

    finally :
        # Delete cursor and row objects to remove locks on the data 
        if not newRow is None : 
            del newRow 
        if not newRows is None : 
            del newRows


