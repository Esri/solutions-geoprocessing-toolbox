#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------
# Name: ProcessInfo.py
# Description: Class to read in process values from MDCS parameter/configuration XML file.
# Version: 20140417
# Requirements: ArcGIS 10.1 SP1
# Author: Esri Imagery Workflows team
#------------------------------------------------------------------------------
#!/usr/bin/env python
from xml.dom import minidom
import os
import Base

class ProcessInfo(Base.Base):

    def __init__(self, base=None):
        self.m_hsh_parent_child_nodes = \
        {
            'addindex' :
                {   'parent' : 'addindex',
                    'child' : 'index'
                },
            'calculatevalues' :
                {   'parent' : 'calculatevalues',
                    'child' : 'calculatevalue'
                }
        }

        self.hasProcessInfo = False
        self.userProcessInfoValues  = False

        self.processInfo = {}
        self.userProcessInfo = {}

        self.m_base = base
        self.setLog(base.m_log)
        self.processInfo = {}
        self.userProcessInfo = {}

        self.hasProcessInfo = False
        self.userProcessInfoValues  = False


    def getXML(self):
        if (self.m_base.m_doc != None
        and self.config != ''):
            return self.m_base.m_doc.toxml()


    def updateProcessInfo(self, pInfo):
            self.userProcessInfoValues = True
            self.userProcessInfo = pInfo
            return self.init(self.config)

    def init(self, config):

        self.config = config
        self.processInfo = {}
        self.hasProcessInfo = False

        Nodelist = self.m_base.m_doc.getElementsByTagName("MosaicDataset")
        if (Nodelist.length == 0):
            self.log ("Error: <MosaicDataset> node is not found! Invalid schema.",
            self.const_critical_text)
            return False

        try:
            for node in Nodelist[0].childNodes:
                  node =  node.nextSibling
                  if (node != None and node.nodeType == minidom.Node.ELEMENT_NODE):

                                if(node.nodeName == 'Processes'):

                                    for node in node.childNodes:
                                        if (node != None and
                                            node.nodeType == minidom.Node.ELEMENT_NODE):

                                            procesName = node.nodeName
                                            procesName = procesName.lower()

                                            if (procesName in self.m_hsh_parent_child_nodes.keys()):
                                                parentNode  = self.m_hsh_parent_child_nodes[procesName]['parent']
                                                childNode = self.m_hsh_parent_child_nodes[procesName]['child']

                                                if ((parentNode in self.processInfo.keys()) == False):
                                                    self.processInfo[parentNode] = []

                                                aryCV = []

                                                for node in node.childNodes:
                                                    if (node != None and node.nodeType == minidom.Node.ELEMENT_NODE):

                                                        key = node.nodeName.lower()
                                                        if (key == childNode):
                                                            hashCV = {}

                                                            for node in node.childNodes:
                                                                if (node != None and node.nodeType == minidom.Node.ELEMENT_NODE):
                                                                    keyName = node.nodeName.lower()
                                                                    value = '#'     #set GP tool default value for argument.
                                                                    try:
                                                                        value = node.firstChild.nodeValue
                                                                    except:
                                                                        Warning_ = True
                                                                    hashCV[keyName] = value
                                                            aryCV.append (hashCV)
                                                self.processInfo[parentNode].append(aryCV)
                                                continue


                                            if ((procesName in self.processInfo.keys()) == False):
                                                self.processInfo[procesName] = []

                                            hashCV = {}
                                            for node in node.childNodes:
                                                if (node != None and node.nodeType == minidom.Node.ELEMENT_NODE):

                                                    key = node.nodeName
                                                    key = key.lower()

                                                    value = '#'     #set GP tool default value for argument.
                                                    try:
                                                        if (self.userProcessInfoValues):
                                                            value = self.userProcessInfo[procesName][key]
                                                            if (value == '#'):
                                                                value = ''
                                                            if (node.childNodes.length == 0):
                                                                node.appendChild(self.m_base.m_doc.createTextNode(value))
                                                            node.firstChild.nodeValue = value

                                                        value = node.firstChild.nodeValue
                                                    except:
                                                        Warning_ = True

                                                    hashCV[key] = value
                                            self.processInfo[procesName].append(hashCV)

        except Exception as inst:
            self.log ("Error: Reading <MosaicDataset> node.",
            self.const_critical_text)
            return False

        if (len (self.processInfo) > 0):
            self.hasProcessInfo = True

        self.userProcessInfoValues = False

        return True


