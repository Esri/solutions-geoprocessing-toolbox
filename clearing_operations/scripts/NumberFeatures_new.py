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
 NumberFeatures_new.py
 --------------------------------------------------
 requirements: ArcGIS X.X, Python 2.7 or Python 3.x
 author: ArcGIS Solutions
 contact: support@esri.com
 company: Esri
 ==================================================
 description: 
 GRG Tool logic module. 
 Supports ClearingOperationsTools.pyt
 ==================================================
 history:
 9/6/2017 - mf - original coding
 ==================================================
'''


import os
import sys
import traceback
import arcpy
from arcpy import env
import Utilities

class NumberFeatures(object):
    '''
    '''
    def __init__(self):
        ''' Number Features constructor '''
        self.label = "Number Features"
        self.description = "Number input point features within a selected area."