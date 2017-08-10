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
# WriteMessageFile.py
# Description: Converts Military Feature Class to XML file
# Requirements: ArcGIS Desktop Standard
#----------------------------------------------------------------------------------

import arcpy
import DictionaryConstants
import MilitaryUtilities
import re
import os
import tempfile
import traceback
import uuid

### Params:
### 0 - inputFC
### 1 - outputXMLFile
### 2 - symbology standard (2525, APP6)
### 3 - MessageType field
### 4 - orderBy see: http://resources.arcgis.com/en/help/main/10.1/index.html#//018v00000050000000)
###     orderBy now called sort_fields (ex: sort_fields="STATE_NAME A; POP2000 D")
### 5 - disable geometry transformation

appendFile = False
DEBUG_GEOMETRY_CONVERSION = False # switch to bypass geometry conversion to keep feature at original placement
foundEmptySIDC = False  # used to detect if any rows are found without SIDC set

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# TODO / IMPORTANT : This flag may need to be set to false when using with Simulator Messages
# If false, it will reuse/map the ID/GUID for each UniqueDesignation
FORCE_UNIQUE_IDs = True 
# When set to "True" it forces the creation of new IDs for each row, when not using Simulation Messages 
# and we want every row to show up, even if someone accidentally used the same "Unique" Designation
# (this was the case with the Test Data provided)
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def writeMessageFile() :
    
    global DEBUG_GEOMETRY_CONVERSION, appendFile, foundEmptySIDC, FORCE_UNIQUE_IDs

    try :
        arcpy.AddMessage("Starting: Write/Append Message File")

        # Get input feature class
        inputFC = arcpy.GetParameter(0)
        if (inputFC == "") or (inputFC is None):
            inputFC = os.path.join(MilitaryUtilities.geoDatabasePath, r"/test_inputs.gdb/FriendlyOperations/FriendlyUnits")
        desc = arcpy.Describe(inputFC)
        if desc == None :
            arcpy.AddError("Bad Input Feature Class")
            return

        shapeType = desc.shapeType
        
        # Get output filename
        outputFile = arcpy.GetParameterAsText(1)
        
        # Get standard
        standard = arcpy.GetParameterAsText(2)
        
        # Message Type Field
        messageTypeField = arcpy.GetParameterAsText(3)   
        
        # Sort Order 
        orderBy = arcpy.GetParameterAsText(4)       
        
        # Disable Geo Transformation and use default SIDC
        disableGeoTransform = arcpy.GetParameterAsText(5)
        if not ((disableGeoTransform == "") or (disableGeoTransform is None)) :
            DEBUG_GEOMETRY_CONVERSION = (disableGeoTransform.upper() == "TRUE")       

        arcpy.AddMessage("Running with Parameters:")
        arcpy.AddMessage("0 - Input FC: " + str(inputFC))
        arcpy.AddMessage("1 - outputXMLFile: " + str(outputFile))
        arcpy.AddMessage("2 - symbology standard: " + str(standard))        
        arcpy.AddMessage("3 - MessageTypeField: " + messageTypeField)
        arcpy.AddMessage("4 - orderBy: " + orderBy)
        arcpy.AddMessage("5 - disableGeoTransform: " + disableGeoTransform)
        
        # initialize the standard
        MilitaryUtilities.getGeometryConverterStandard(standard)
        
        if DEBUG_GEOMETRY_CONVERSION : 
            arcpy.AddWarning("Running in Debug Geo-Transformation Mode, symbol will use default/unknown SIDC for shape")
        
        if not ((messageTypeField == "") or (messageTypeField is None)) :
            # make sure the messageTypeField exists in the input
            if messageTypeField in [field.name for field in desc.Fields] :
                MilitaryUtilities.MessageTypeField = messageTypeField
            else :
                arcpy.AddWarning("MessageTypeField does not exist in input: " + messageTypeField + " , using default")
        
        # Check Output Filename & see handle case if we are appending
        if (outputFile == "") or (outputFile is None) :
            # For a standalone test (debug) if no output filename provided
            if DEBUG_GEOMETRY_CONVERSION : 
                defaultOutputName = "Mil2525CMessages-NoTransform.xml"
            else : 
                defaultOutputName = "Mil2525CMessages.xml"   
            outputFile = os.path.join(os.path.dirname(__file__), defaultOutputName)  
            messageFile=open(outputFile, "w")
            arcpy.AddWarning("No Output set, using default: " + str(outputFile))
        else:            
            arcpy.AddMessage("Append File set to " + str(appendFile))
            if (not appendFile) :
                messageFile = open(outputFile, "w")
            elif (not os.path.isfile(outputFile)) :
                arcpy.AddWarning("Can't Append: Output File does not exist, creating new file")
                messageFile = open(outputFile, "w")                
            else :
                arcpy.AddMessage("Appending Existing File...")
                
                # Appending the file is a bit more complicated because we have to remove the 
                # "</messages>" from the end of the original file therefore it can't just be 
                # opened as an append "a+"-we have to create a temp file, read the original file in,
                # except for the line "</messages>", and then write back out
                
                fileToAppend = open(outputFile, "r")
                # Workaround/Note: didn't work in ArcCatalog unless I opened temp file this way
                temporaryFile = tempfile.NamedTemporaryFile(mode="w", delete=False)

                # Copy the file line by line, but don't include last end tag ex. </messages>
                finalTag = "</%s>" % MilitaryUtilities.getMessageRootTag()
                finalTagFound = False
                while True:
                    line = fileToAppend.readline()
                    if line : 
                        if not finalTag in line :  # ex. "</messages>"
                            temporaryFile.write(line)
                        else :
                            finalTagFound = True
                    else :
                        break

                if (not finalTagFound) : 
                    arcpy.AddError("XML Append File will be corrupt: Could not find Tag: " + finalTag)
                    
                # now write those lines back
                fileToAppend.close()
                temporaryFile.close()
                messageFile = open(outputFile, "w")
                temporaryFile = open(temporaryFile.name, "r")
                while True:
                    line = temporaryFile.readline()
                    if line : 
                        messageFile.write(line)
                    else :
                        break

                temporaryFile.close()

        if (messageFile is None) : 
            arcpy.AddError("Output file can't be created, exiting")
            return
        
        ##################Setup for export############################

        # We need to set overwriteOutput=true or the tools below may fail
        previousOverwriteOutputSetting = arcpy.env.overwriteOutput
        arcpy.env.overwriteOutput = True
        
        # Densify if this is a polygon FC
        if ("Polygon" == shapeType):
            try : 
                densifiedFC = "in_memory/DensifiedFC"
                arcpy.CopyFeatures_management(inputFC, densifiedFC)
                arcpy.Densify_edit(densifiedFC, "ANGLE", "", "", 10)
                inputFC = densifiedFC
            except :
                arcpy.AddWarning("Could not densify polygons, skipping. Densify_edit tool failed - is Desktop Standard License available?")
              
        # Get fields and coded domains
        CODE_FIELD_NAME = "code"
        DESCRIPTION_FIELD_NAME = "description"
        fieldNameList = []
        fieldNameToDomainName = {}
        for field in desc.Fields:
            if not (field.name in DictionaryConstants.MILFEATURES_FIELD_EXCLUDE_LIST):
                fieldNameList.append(field.name)
                # Get domain if any
                if (field.domain is not None and field.domain != ""):
                    fieldNameToDomainName[field.name] = field.domain
                    dataPath = desc.path
                    gdbPath = dataPath.split(".gdb")[0]
                    gdbPath += ".gdb"
                    arcpy.DomainToTable_management(gdbPath, field.domain, "in_memory/" + field.domain, CODE_FIELD_NAME, DESCRIPTION_FIELD_NAME)

        # print fieldNameList

        # restore this setting (set above)
        arcpy.env.overwriteOutput = previousOverwriteOutputSetting
        
        # Projected or geographic?
        xname = "lon"
        yname = "lat"
        isProjected = desc.spatialReference.type == "Projected"
        if (isProjected):
            xname = "x"
            yname = "y"
        wkid = desc.spatialReference.factoryCode

        ################Begin Export ##########################

        # Open a search cursor (if possible)
        try :            
            rows = arcpy.SearchCursor(inputFC, "", "", "", orderBy)            
        except :            
            arcpy.AddError("Could not open Feature Class " + str(inputFC))
            if (not ((orderBy == "") and not (orderBy is None))) :
                arcpy.AddError("OrderBy Search Option: " + orderBy)
            raise Exception("Bad Feature Class Input")             

        # Dictionary to map unique designation to ID
        unitDesignationToId = dict()
        
        featureFields = desc.fields

        ###################### Write XML file #########################

        if not appendFile :
            # Ex: Next line writes: messageFile.write("<geomessages>\n") 
            messageFile.write("<%s>\n" % MilitaryUtilities.getMessageRootTag())            
            
        rowCount = 0

        # Iterate through the rows in the cursor
        for row in rows:
            shape = row.shape.getPart(0)
    
            arcpy.AddMessage("Processing row: " + str(rowCount))
            
            ##############################################
            # Map Unique Names to same Unique IDs
            # IMPORTANT: this section tries to keep Unique Designations mapped to the 
            #            same Message Unique ID (so they will move in Message Processor), so...
            # WARNING: if you have repeated Unique Designations,
            #            they are going to get mapped to the same Unique ID             
            uniqueId = "{%s}" % str(uuid.uuid4())
            uniqueDesignation = str(rowCount) # fallback value in case field does not exist            
            
            try :
                uniqueDesignation = row.getValue(MilitaryUtilities.UniqueDesignationField)
 
                if ((uniqueDesignation is None) or (uniqueDesignation == "")) :
                    arcpy.AddWarning("Unique Designation is Empty")                     
                elif (DEBUG_GEOMETRY_CONVERSION or FORCE_UNIQUE_IDs) :                   
                    pass 
                else :   
                    # Otherwise, see if we have seen this Designation before
                    if (uniqueDesignation in unitDesignationToId):
                        arcpy.AddMessage("Creating update message for repeated Unique Designation: " + uniqueDesignation)
                        uniqueId = unitDesignationToId[uniqueDesignation]
                    else:
                        unitDesignationToId[uniqueDesignation] = uniqueId
            except:
                arcpy.AddWarning("Could not find Unique Designation field in row: " + str(rowCount))                                    
            ##############################################

            # work with "sidc" or "sic"
            try : 
                SymbolIdCodeVal = row.getValue(MilitaryUtilities.SidcFieldChoice1) # "sic"
            except:
                try : 
                    SymbolIdCodeVal = row.getValue(MilitaryUtilities.SidcFieldChoice2) # "sidc"
                except:     
                    SymbolIdCodeVal = None                

            # Note/Important: attributes need to be set in converter so needs declared before geometrytoControlPoints
            attributes = { } 
            conversionNotes = None
            attributes[DictionaryConstants.Tag_Wkid] = wkid  # needed by conversion
                                  
            if (SymbolIdCodeVal is None) or (SymbolIdCodeVal == "") : 
                SymbolIdCodeVal = DictionaryConstants.getDefaultSidcForShapeType(shapeType)
                if not (DEBUG_GEOMETRY_CONVERSION) :
                    foundEmptySIDC = True
                    msg =  "SIDC is not set, using default: " + SymbolIdCodeVal
                    arcpy.AddWarning(msg)
            # TODO: we may need to add an option to Disable the geometry conversion
            # *but* not to change the SIDC to the default one, if you don't want the SIDC to change
            # when "Disable Geometry Conversion" is checked, comment/uncomment thses lines to
            # set this to false/disable this behavior:
            # elif False :
            elif DEBUG_GEOMETRY_CONVERSION :
                print "Using Debug SIDC"
                conversionNotes = "Original SIDC: " + SymbolIdCodeVal
                uniqueDesignation = SymbolIdCodeVal # use this label for debugging
                SymbolIdCodeVal = DictionaryConstants.getDefaultSidcForShapeType(shapeType)

            controlPointsString = MilitaryUtilities.parseGeometryToControlPoints(shape)
            requiresConversion = MilitaryUtilities.geoConverter.requiresConversion(SymbolIdCodeVal)
            if requiresConversion and not DEBUG_GEOMETRY_CONVERSION :                
                msg = "SIC: " + SymbolIdCodeVal + " requires conversion/translation"
                print msg
                arcpy.AddMessage(msg)
                transformedPoints, conversionNotes = \
                    MilitaryUtilities.geoConverter.geometrytoControlPoints(SymbolIdCodeVal, controlPointsString, attributes)                
                if (conversionNotes == DictionaryConstants.CONVERSION_IGNORE_SECOND_LINE) : 
                    continue
                elif (transformedPoints is None) :
                    arcpy.AddWarning("Conversion FAILED for SIC: " + SymbolIdCodeVal + \
                                     ", Notes: " + conversionNotes + " (using original points)")
                else :
                    controlPointsString = transformedPoints

            # Write Output Message
            # Ex: Next line writes: ex. "\t<geomessage v=\"1.0\">\n"            
            messageFile.write("\t<%s v=\"%s\">\n" % (MilitaryUtilities.getMessageTag(), \
                                                     MilitaryUtilities.getMessageVersion()))
            
            messageFile.write("\t\t<sic>%s</sic>\n" % SymbolIdCodeVal) 

            # Try to get a message type if the field exists
            try :   
                messageTypeVal = row.getValue(MilitaryUtilities.MessageTypeField)           
                messageFile.write("\t\t<_type>%s</_type>\n" % messageTypeVal)
            except :             
                # if not default to position_report
                messageFile.write("\t\t<_type>%s</_type>\n" % DictionaryConstants.DefaultMessageType)       
                                 
            ##TODO: see if other actions are valid besides just "update"
            messageFile.write("\t\t<_action>%s</_action>\n" % DictionaryConstants.DefaultMessageAction) # = update
            
            messageFile.write("\t\t<_id>%s</_id>\n" % uniqueId) 
            messageFile.write("\t\t<_control_points>%s</_control_points>\n" % controlPointsString)  
            if not ((conversionNotes is None) or (conversionNotes == "")) : 
                messageFile.write("\t\t<ConversionNotes>%s</ConversionNotes>\n" % conversionNotes)

            # Note: written with attributes below: messageFile.write("\t\t<_wkid>%i</_wkid>\n" % wkid)
                     
            if not ((uniqueDesignation is None) or (uniqueDesignation == "")) : 
                messageFile.write("\t\t<%s>%s</%s>\n" % (DictionaryConstants.Tag_UniqueDesignation, \
                             uniqueDesignation, DictionaryConstants.Tag_UniqueDesignation))
                     

            # Check on Military Geometries for Lines/Areas
            if (shapeType is "Point"):
                messageFile.write("\t\t<altitude_depth>%d</altitude_depth>\n" % shape.Z)

            rowCount = rowCount + 1
            messageFile.write("\t\t<MessageCount>%s</MessageCount>\n" % str(rowCount))             

            for key in attributes :
                attrValAsString = str(attributes[key])
                messageFile.write("\t\t<"+key+">" + attrValAsString + "</" + key + ">\n")

            ###################Common Fields/Attributes#####################
            
            # Write out remaining table fields as Tag attributes
            for field in fieldNameList:
                try : 
                    # But don't repeat existing tags we've created
                    if field in DictionaryConstants.MESSAGES_TAG_LIST :
                        rowVal = None 
                    else :
                        rowVal = row.getValue(field)
                except :
                    print "Could not get row val for field" + field
                    rowVal = None
                    
                if (rowVal is not None) and (rowVal != '') :
                    try:
						fieldValAsString = str(row.getValue(field))
						messageFile.write("\t\t<"+field+">" + fieldValAsString + "</" + field + ">\n")
                    except:
                        #fixed issue #19
						fieldValAsString = row.getValue(field)
						decodedstring = fieldValAsString.encode('ascii', 'ignore')
						arcpy.AddMessage("trying to fix unicode problem, changing " + fieldValAsString + " -> " + decodedstring)
						messageFile.write("\t\t<"+field+">" + decodedstring + "</" + field + ">\n")
						
            ###################Common Fields/Attributes#####################

            # Ex: messageFile.write("\t</geomessage>\n")
            messageFile.write("\t</%s>\n" % MilitaryUtilities.getMessageTag())

        # Ex: messageFile.write("</geomessages>")
        messageFile.write("</%s>\n" % MilitaryUtilities.getMessageRootTag())
            
        arcpy.AddMessage("Rows Processed: " + str(rowCount))   
        if foundEmptySIDC :
            arcpy.AddWarning("IMPORTANT: Some rows did not have SIDC set - you may need to run CalcSIDCField tool first.")
        arcpy.AddMessage("Write/Append Message File Complete")
        
    except: 
        print "Exception: " 
        tb = traceback.format_exc()
        print tb
        arcpy.AddError("Exception")
        arcpy.AddError(tb)
