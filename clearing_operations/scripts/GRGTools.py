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
 GRGTools.py
 --------------------------------------------------
 requirements: ArcGIS X.X, Python 2.7 or Python 3.x
 author: ArcGIS Solutions
 contact: support@esri.com
 company: Esri
 ==================================================
 description:
 GRG Tool logic module.
 Supports GRGTools.pyt and uses GRGUtilities.py
 ==================================================
 history:
 9/1/2017 - mf - original coding
 ==================================================
'''

import os
import sys
import traceback
import arcpy
from arcpy import env
import GRGUtilities

class CreateGRGFromArea(object):
    '''
    Create a Gridded Reference Graphic (GRG) from an selected area on the map.
    '''
    def __init__(self):
        '''
        '''
        self.label = "Create GRG from Area"
        self.description = "Create a Gridded Reference Graphic (GRG) from an selected area on the map."

    def getParameterInfo(self):
        '''
        Define parameter definitions
        '''

        # TODO: Set input as Feature Set from method
        input_area_features = arcpy.Parameter(name='input_canvas_area',
                                              displayName='Input GRG Area',
                                              direction='Input',
                                              datatype='GPFeatureRecordSetLayer',
                                              parameterType='Required',
                                              enabled=True,
                                              multiValue=False)
        input_area_features.value = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                 "layers","GRGInputArea.lyr")

        cell_width = arcpy.Parameter(name='cell_width',
                                     displayName='Cell Width',
                                     direction='Input',
                                     datatype='GPDouble',
                                     parameterType='Required',
                                     enabled=True,
                                     multiValue=False)
        cell_width.value = 100.0

        cell_height = arcpy.Parameter(name='cell_height',
                                      displayName='Cell Height',
                                      direction='Input',
                                      datatype='GPDouble',
                                      parameterType='Required',
                                      enabled=True,
                                      multiValue=False)
        cell_height.value = 100.0

        cell_units = arcpy.Parameter(name='cell_units',
                                     displayName='Cell Units',
                                     direction='Input',
                                     datatype='GPString',
                                     parameterType='Required',
                                     enabled=True,
                                     multiValue=False)
        cell_units.filter.type = 'ValueList'
        cell_units.filter.list = ['METERS', 'FEET']
        cell_units.value = cell_units.filter.list[0]

        label_start_position = arcpy.Parameter(name='label_start_position',
                                               displayName='Label Start Position',
                                               direction='Input',
                                               datatype='GPString',
                                               parameterType='Required',
                                               enabled=True,
                                               multiValue=False)
        label_start_position.filter.type = 'ValueList'
        label_start_position.filter.list = ['UPPER_RIGHT',
                                            'LOWER_RIGHT',
                                            'UPPER_LEFT',
                                            'LOWER_LEFT']
        label_start_position.value = label_start_position.filter.list[0]

        label_style = arcpy.Parameter(name='label_style',
                                      displayName='Label Style',
                                      direction='Input',
                                      datatype='GPString',
                                      parameterType='Required',
                                      enabled=True,
                                      multiValue=False)
        label_style.filter.type = 'ValueList'
        label_style.filter.list = ['ALPHA-ALPHA',
                                   'ALPHA-NUMERIC',
                                   'NUMERIC-NUMERIC']
        label_style.value = label_style.filter.list[0]

        # TODO: define output schema as method
        output_features= arcpy.Parameter(name='output_grg-features',
                                         displayName='Output GRG Features',
                                         direction='Output',
                                         datatype='DEFeatureClass',
                                         parameterType='Required',
                                         enabled=True,
                                         multiValue=False)
        output_features.value = r"%scratchGDB%/area_grg"

        return [input_area_features,
                cell_width,
                cell_height,
                cell_units,
                label_start_position,
                label_style,
                output_features]

    def updateParameters(self, parameters):
        '''
        Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed.
        '''
        return

    def updateMessages(self, parameters):
        '''
        '''
        return

    def execute(self, parameters, messages):
        ''' execute for toolbox'''
        #arcpy.AddError("Not built yet.")
        out_grg = GRGUtilities.GRGFromArea(parameters[0].value,
                                           parameters[1].value,
                                           parameters[2].value,
                                           parameters[3].value,
                                           parameters[4].value,
                                           parameters[5].value,
                                           parameters[6].value)
        return out_grg

class CreateGRGFromPoint(object):
    '''
    Create a Gridded Reference Graphic (GRG) from an selected location on the map.
    '''
    def __init__(self):
        ''' Point Target GRG constructor '''
        self.label = "Create GRG from Point"
        self.description = "Create a Gridded Reference Graphic (GRG) from an selected location on the map."

    def getParameterInfo(self):
        '''
        Define parameter definitions
        '''

        # TODO: Set input as Feature Set from method
        input_start_location = arcpy.Parameter(name='input_start_location',
                                              displayName='Input Start Location',
                                              direction='Input',
                                              datatype='GPFeatureRecordSetLayer',
                                              parameterType='Required',
                                              enabled=True,
                                              multiValue=False)
        input_start_location.value = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                 "layers","GRGInputPoint.lyr")

        horizontal_cells = arcpy.Parameter(name='horizontal_cells',
                                     displayName='Number of Horizontal Grid Cells',
                                     direction='Input',
                                     datatype='GPDouble',
                                     parameterType='Required',
                                     enabled=True,
                                     multiValue=False)
        horizontal_cells.value = 10

        vertical_cells = arcpy.Parameter(name='vertical_cells',
                                         displayName='Number of Vertical Grid Cells',
                                         direction='Input',
                                         datatype='GPDouble',
                                         parameterType='Required',
                                         enabled=True,
                                         multiValue=False)
        vertical_cells.value = 10

        cell_width = arcpy.Parameter(name='cell_width',
                                     displayName='Cell Width',
                                     direction='Input',
                                     datatype='GPDouble',
                                     parameterType='Required',
                                     enabled=True,
                                     multiValue=False)
        cell_width.value = 100.0

        cell_height = arcpy.Parameter(name='cell_height',
                                      displayName='Cell Height',
                                      direction='Input',
                                      datatype='GPDouble',
                                      parameterType='Required',
                                      enabled=True,
                                      multiValue=False)
        cell_height.value = 100.0

        cell_units = arcpy.Parameter(name='cell_units',
                                     displayName='Cell Units',
                                     direction='Input',
                                     datatype='GPString',
                                     parameterType='Required',
                                     enabled=True,
                                     multiValue=False)
        cell_units.filter.type = 'ValueList'
        cell_units.filter.list = ['METERS', 'FEET']
        cell_units.value = cell_units.filter.list[0]

        label_start_position = arcpy.Parameter(name='label_start_position',
                                               displayName='Label Start Position',
                                               direction='Input',
                                               datatype='GPString',
                                               parameterType='Required',
                                               enabled=True,
                                               multiValue=False)
        label_start_position.filter.type = 'ValueList'
        label_start_position.filter.list = ['UPPER_RIGHT',
                                            'LOWER_RIGHT',
                                            'UPPER_LEFT',
                                            'LOWER_LEFT']
        label_start_position.value = label_start_position.filter.list[0]

        label_style = arcpy.Parameter(name='label_style',
                                      displayName='Label Style',
                                      direction='Input',
                                      datatype='GPString',
                                      parameterType='Required',
                                      enabled=True,
                                      multiValue=False)
        label_style.filter.type = 'ValueList'
        label_style.filter.list = ['ALPHA-ALPHA',
                                   'ALPHA-NUMERIC',
                                   'NUMERIC-NUMERIC']
        label_style.value = label_style.filter.list[0]

        # TODO: define output schema as method
        output_features= arcpy.Parameter(name='output_grg-features',
                                         displayName='Output GRG Features',
                                         direction='Output',
                                         datatype='DEFeatureClass',
                                         parameterType='Required',
                                         enabled=True,
                                         multiValue=False)
        output_features.value = r"%scratchGDB%/point_grg"

        return [input_start_location,
                horizontal_cells,
                vertical_cells,
                cell_width,
                cell_height,
                cell_units,
                label_start_position,
                label_style,
                output_features]

    def updateParameters(self, parameters):
        '''
        Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed.
        '''
        return

    def updateMessages(self, parameters):
        '''
        '''
        return

    def execute(self, parameters, messages):
        ''' execute for toolbox'''
        arcpy.AddError("Not built yet.")

        # out_grg = GRGUtilities.GRGFromPoint(starting_point=parameters[0],
        #                                     horizontal_cells=parameters[1],
        #                                     vertical_cells=parameters[2],
        #                                     cell_width=parameters[3],
        #                                     cell_height=parameters[4],
        #                                     cell_units=parameters[5],
        #                                     label_start_position=parameters[6],
        #                                     label_style=parameters[7],
        #                                     output_feature_class=parameters[8])
        return #out_grg

def _outputGRGSchema():
    ''' '''
    # TODO: implement output schema for all GRG features
    return None