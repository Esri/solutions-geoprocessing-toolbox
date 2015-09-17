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
# Name: SetMDProperties.py
# Description: To set mosaic dataset properties
# Version: 20150405
# Requirements: ArcGIS 10.1 SP1
# Author: Esri Imagery Workflows team
#------------------------------------------------------------------------------
#!/usr/bin/env python

import arcpy,os,sys
from xml.dom import minidom
import Base

class SetMDProperties(Base.Base):

    def __init__(self, base):
        self.dic_properties_lst = {}
        self.dicMDs = {}

        self.setLog(base.m_log)
        self.m_base = base


    def is101SP1(self):
        return self.CheckMDCSVersion([10, 1, 0, 0], [0, 0, 0, 0])       # ver [major, minor, revision, build]


    def getInternalPropValue(self, md, key):
        if (key in self.dic_properties_lst.keys()):
            return self.dic_properties_lst[key]
        else:
            return ''

    def __message(self, msg, type):
        self.log(msg, type)

    def __setpropertiesCallback(self, args, fn_name):
        CONST_ORDER_FIELD_POS = 16
        if (self.is101SP1() == False):  #OrderField set to 'BEST' would fail in 10.1 without SP1
            args[CONST_ORDER_FIELD_POS] = 'MinPS'
        return args

    def setMDProperties(self, mdPath):
        args = []
        mdName = os.path.basename(mdPath).upper()
        args.append(mdPath)
        args.append(self.getInternalPropValue(mdName, 'rows_maximum_imagesize'))
        args.append(self.getInternalPropValue(mdName, 'columns_maximum_imagesize'))
        args.append(self.getInternalPropValue(mdName, 'allowed_compressions'))
        args.append(self.getInternalPropValue(mdName,'default_compression_type'))
        args.append(self.getInternalPropValue(mdName,'JPEG_quality'))
        args.append(self.getInternalPropValue(mdName,'LERC_Tolerance'))
        args.append(self.getInternalPropValue(mdName,'resampling_type'))
        args.append(self.getInternalPropValue(mdName,'clip_to_footprints'))
        args.append(self.getInternalPropValue(mdName,'footprints_may_contain_nodata'))
        args.append(self.getInternalPropValue(mdName,'clip_to_boundary'))
        args.append(self.getInternalPropValue(mdName,'color_correction'))
        args.append(self.getInternalPropValue(mdName,'allowed_mensuration_capabilities'))
        args.append(self.getInternalPropValue(mdName,'default_mensuration_capabilities'))
        args.append(self.getInternalPropValue(mdName,'allowed_mosaic_methods'))
        args.append(self.getInternalPropValue(mdName, 'default_mosaic_method'))
        args.append(self.getInternalPropValue(mdName, 'Order_field'))
        args.append(self.getInternalPropValue(mdName,'order_base'))
        args.append(self.getInternalPropValue(mdName,'sorting_order'))
        args.append(self.getInternalPropValue(mdName,'mosaic_operator'))
        args.append(self.getInternalPropValue(mdName, 'blend_width'))
        args.append(self.getInternalPropValue(mdName, 'view_point_x'))
        args.append(self.getInternalPropValue(mdName,'view_point_y'))
        args.append(self.getInternalPropValue(mdName, 'max_num_per_mosaic'))
        args.append(self.getInternalPropValue(mdName,'cell_size_tolerance'))
        args.append(self.getInternalPropValue(mdName, 'cell_size'))
        args.append(self.getInternalPropValue(mdName, 'metadata_level'))
        args.append(self.getInternalPropValue(mdName,'transmission_fields'))
        args.append(self.getInternalPropValue(mdName,'use_time'))
        args.append(self.getInternalPropValue(mdName,'start_time_field'))
        args.append(self.getInternalPropValue(mdName,'end_time_field'))
        args.append(self.getInternalPropValue(mdName, 'time_format'))
        args.append(self.getInternalPropValue(mdName,'geographic_transform'))
        args.append(self.getInternalPropValue(mdName, 'max_num_of_download_items'))
        args.append(self.getInternalPropValue(mdName,'max_num_of_records_returned'))
        args.append(self.getInternalPropValue(mdName,'data_source_type'))
        args.append(self.getInternalPropValue(mdName,'minimum_pixel_contribution'))
        args.append(self.getInternalPropValue(mdName,'processing_templates'))
        args.append(self.getInternalPropValue(mdName,'default_processing_template'))

        setProperties = Base.DynaInvoke('arcpy.SetMosaicDatasetProperties_management', args, self.__setpropertiesCallback, self.__message)
        if (setProperties.init() == False):
            return False
        return setProperties.invoke()


    def init(self, config):

        Nodelist = self.m_base.m_doc.getElementsByTagName("MosaicDataset")
        if (Nodelist.length == 0):
            self.log("Error: MosaicDataset node not found! Invalid schema.", self.const_critical_text)
            return False

        try:
            for node in Nodelist[0].childNodes:
                  node =  node.nextSibling
                  if (node != None and node.nodeType == minidom.Node.ELEMENT_NODE):
                        if (node.nodeName == 'DefaultProperties'):
                            for node in node.childNodes:
                                if (node.nodeType == minidom.Node.ELEMENT_NODE):
                                    if node.nodeName == 'processing_templates' or node.nodeName == 'default_processing_template':
                                        ptvalue = node.firstChild.nodeValue
                                        if ptvalue != '#':
                                            ptvaluesplit = ptvalue.split(';')
                                            rftpaths = ''
                                            for each in ptvaluesplit:
                                                if each.find('/') == -1:
                                                    if each.lower() == 'none':
                                                        rftpaths = rftpaths + each + ";"
                                                    else:
                                                        rftpaths = rftpaths + os.path.abspath(os.path.join((self.m_base.const_raster_function_templates_path_),each)) +";"
                                            rftpaths = rftpaths[:-1]
                                            self.dic_properties_lst[node.nodeName] = rftpaths
                                        else:
                                            self.dic_properties_lst[node.nodeName] = ptvalue
                                    else:

                                        self.dic_properties_lst[node.nodeName] = node.firstChild.nodeValue

        except:
            Error = True

        return True 
