# coding: utf-8
'''
------------------------------------------------------------------------------
 Copyright 2017 Esri
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
------------------------------------------------------------------------------
 ==================================================
 ClearingOperationsTools.pyt
 --------------------------------------------------
 requirements: ArcGIS 10.3.1+, ArcGIS Pro 1.4+
 author: ArcGIS Solutions
 contact: support@esri.com
 company: Esri
 ==================================================
 description:
 Python toolbox container for Clearing Operations tools.
 ==================================================
 history:
 09/06/2017 - mf - original coding
 ==================================================
'''

from scripts.GRGTools import *
from scripts.NumberFeaturesTool import *

class Toolbox(object):
    '''
    Clearing Operations Toolbox class container.
    '''

    def __init__(self):
        ''' constructor '''
        self.label = "Clearing Operations Tools"
        self.alias = "clrops"
        self.description = r'''
                           The Clearing Operations Tools supports area mapping operations 
                           with tools to systematically number structures and create custom 
                           Gridded Reference Graphics (GRG).
                           '''
        self.tools = [CreateGRGFromArea,
                      CreateGRGFromPoint,
                      NumberFeatures]
