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
# Name: CreateMD.py
# Description: Creates source mosaic datasets.
# Version: 20140417
# Requirements: ArcGIS 10.1 SP1
# Author: Esri Imagery Workflows team
#------------------------------------------------------------------------------
#!/usr/bin/env python

import arcpy,os,sys
from xml.dom import minidom

import Base

class CreateMD(Base.Base):
    def __init__(self, base):

        self.srs = ''
        self.pixel_type = ''
        self.product_definition = ''
        self.num_bands = ''
        self.product_band_definitions = ''

        self.setLog(base.m_log)
        self.m_base = base


    def createGeodataBase(self):
        if (self.m_base.m_IsSDE == True):       # MDCS doesn't create new SDE connections and assumes .SDE connection passed on exists @ the server
            return True                         # to create new Mosaic Datasets.

        # create output workspace if missing.
        if (os.path.exists(self.m_base.m_workspace) == False):
            try:
                os.makedirs(self.m_base.m_workspace)
            except:
                self.log("Failed to create folder: " + self.m_base.m_workspace, self.const_critical_text)
                self.log(arcpy.GetMessages(), self.const_critical_text)
                return False

        # create Geodatabase
        try:
            self.log('Creating Geodatabase: ({})'.format(self.m_base.m_geoPath), self.const_general_text)
            if not os.path.exists(self.m_base.m_geoPath):
                arcpy.CreateFileGDB_management(self.m_base.m_workspace, self.m_base.m_gdbName)
            else:
                self.log("\t000258: File geodatabase already exists!", self.const_warning_text)
            return True
        except:
            return False


    def createMD(self):
        self.log("Creating source mosaic datasets:", self.const_general_text)

        try:
            mdPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
            if not arcpy.Exists(mdPath):
                self.log("\t" + self.m_base.m_mdName, self.const_general_text)
                arcpy.CreateMosaicDataset_management(self.m_base.m_geoPath,self.m_base.m_mdName,self.srs,self.num_bands,self.pixel_type,self.product_definition,self.product_band_definitions)

        except:
            self.log("Failed!", self.const_critical_text)
            self.log(arcpy.GetMessages(), self.const_critical_text)
            return False

        return True


    def init(self, config):
        Nodelist = self.m_base.m_doc.getElementsByTagName("MosaicDataset")
        if (Nodelist.length == 0):
            self.log("\nError: MosaicDatasets node not found! Invalid schema.", self.const_critical_text)
            return False

        try:
            for node in Nodelist[0].childNodes:
                  node =  node.nextSibling
                  if (node != None and node.nodeType == minidom.Node.ELEMENT_NODE):
                      if(node.nodeName == 'SRS'):
                            self.srs = node.firstChild.nodeValue
                      elif(node.nodeName == 'pixel_type'):
                            self.pixel_type = node.firstChild.nodeValue
                      elif(node.nodeName == 'num_bands'):
                            self.num_bands = node.firstChild.nodeValue
                      elif(node.nodeName == 'product_definition'):
                            self.product_definition = node.firstChild.nodeValue
                      elif(node.nodeName == 'product_band_definitions'):
                            self.product_band_definitions = node.firstChild.nodeValue
        except:
            self.log("\nError: reading MosaicDataset nodes.", self.const_critical_text)
            return False

        return True
