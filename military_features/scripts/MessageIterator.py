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
# MessageIterator.py
# Description: Iterates through an xml file with Runtime/GeoMessage Message format 
#              and returns message tags/values as a dictionary
#----------------------------------------------------------------------------------

import xml.dom.minidom
import os.path
import DictionaryConstants

class MessageIterator:
    
    # The Tag to search for
    MessageTagName = DictionaryConstants.MessageTagName # "geomessage"      # ex. message -or- geomessage
    
    def __init__(self, messageFileName):
        self.messageFileName = messageFileName

        if not os.path.isfile(messageFileName) :
            msg = "File not found: " + messageFileName
            raise IOError(msg)

        doc = xml.dom.minidom.parse(messageFileName)
        self.messageNodes = doc.getElementsByTagName(MessageIterator.MessageTagName) # ex."message"
        self.currentMessageIndex = 0
        self.lastMessageIndex = len(self.messageNodes) - 1

    def getMessageSicControlPointsFromXml(self, messageElementXml) : 

        node = messageElementXml

        if node.nodeType != xml.dom.Node.ELEMENT_NODE :
            return None, None, None
        
        attributes = { }

        # print 'Element name: %s' % node.nodeName

        try : 
            sic = node.getElementsByTagName(DictionaryConstants.Tag_SymbolId)[0].childNodes[0].data
        except :
            print "Warning: No SIDC Tag in Message"
            sic = DictionaryConstants.DEFAULT_POINT_SIDC
            
        try :             
            controlPoints = node.getElementsByTagName(DictionaryConstants.Tag_ControlPoints)[0].childNodes[0].data
        except :
            print "Warning: No ControlPoints Tag in Message"
            controlPoints = "0.0, 0.0"
            
        childNodes = node.getElementsByTagName("*")

        for childNode in childNodes:
            if childNode.nodeType == childNode.ELEMENT_NODE:
                # print childNode.tagName, childNode.childNodes[0].data
                tag = childNode.tagName
                if (not(tag == DictionaryConstants.Tag_SymbolId) \
                    or (tag == DictionaryConstants.Tag_ControlPoints)) :
                    attributes[tag] = childNode.childNodes[0].data

        return sic, controlPoints, attributes

    def __iter__(self) :
        return self

    def next(self) :
        if self.currentMessageIndex > self.lastMessageIndex:
            raise StopIteration
        else:
            node = self.messageNodes[self.currentMessageIndex]
            sic, controlPoints, attributes = self.getMessageSicControlPointsFromXml(node)
            self.currentMessageIndex += 1

            return sic, controlPoints, attributes