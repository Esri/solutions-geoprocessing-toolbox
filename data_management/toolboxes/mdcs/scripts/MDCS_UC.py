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
# Name: MDCS_UC.py
# Description: A class to implement all user functions or to extend the built in MDCS functions/commands chain.
# Version: 20140417
# Requirements: ArcGIS 10.1 SP1
# Author: Esri Imagery Workflows team
#------------------------------------------------------------------------------
#!/usr/bin/env python

import os
import sys
import arcpy

import Base

class UserCode:
    def sample00(self, data):

        base = Base.Base()          # using Base class for its XML specific common functions. (getXMLXPathValue, getXMLNodeValue, getXMLNode)
        xmlDOM = data['mdcs']       # access to MDCS config file
        command_used = base.getXMLNodeValue(xmlDOM, 'Command')

        workspace = data['workspace']
        md = data['mosaicdataset']

        log = data['log']
        log.Message('%s\\%s' % (workspace, md), 0)

        return True



    def sample01(self, data):

        log = data['log']
        log.Message('hello world', 0)

        return True


    def customCV(self, data):

        workspace = data['workspace']
        md = data['mosaicdataset']

        ds = os.path.join(workspace, md)
        ds_cursor = arcpy.UpdateCursor(ds)
        if (ds_cursor != None):
            print ('Calculating values..')
            row = ds_cursor.next()
            while(row != None):
                row.setValue('MinPS', 0)
                row.setValue('MaxPS', 300)

                WRS_Path = row.getValue('WRS_Path')
                WRS_Row = row.getValue('WRS_Row')

                if (WRS_Path != None and
                    WRS_Row != None):
                    PR = (WRS_Path*1000)+WRS_Row
                    row.setValue('PR', PR)


                AcquisitionData = row.getValue('AcquisitionDate')
                if (AcquisitionData != None):
                    AcquisitionData = str(AcquisitionData).replace('-', '/')
                    day = int(AcquisitionData.split()[0].split('/')[1])
                    row.setValue('Month', day)


                grp_name = row.getValue('GroupName')
                if (grp_name != None):
                    CMAX_INDEX = 16
                    if (len(grp_name) >= CMAX_INDEX):
                        row.setValue('DayOfYear', int(grp_name[13:CMAX_INDEX]))
                        row.setValue('Name', grp_name.split('_')[0] + '_' + row.getValue('Tag'))

                ds_cursor.updateRow(row)
                row = ds_cursor.next()

            del ds_cursor


        return True
