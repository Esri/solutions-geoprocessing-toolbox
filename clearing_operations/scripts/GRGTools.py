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
 ==================================================
 history:
 9/1/2017 - mf - original coding
 ==================================================
'''

import os
import arcpy

try:
    from . import GRGUtilities
except ImportError:
    import GRGUtilities
try:
    from . import RefGrid
except ImportError:
    import RefGrid

class CreateGRGFromArea(object):
    '''
    Create a Gridded Reference Graphic (GRG) from an selected area on the map.
    '''
    def __init__(self):
        '''
        Create GRG From Area tool constructor method
        '''
        self.label = "Create GRG from Area"
        self.description = "Create a Gridded Reference Graphic (GRG) from an selected area on the map."

    def getParameterInfo(self):
        '''
        Define parameter definitions
        '''

        input_area_features = arcpy.Parameter(name='input_grg_area',
                                              displayName='Input GRG Area',
                                              direction='Input',
                                              datatype='GPFeatureRecordSetLayer',
                                              parameterType='Required',
                                              enabled=True,
                                              multiValue=False)
        input_layer_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                             "layers",
                                             "RelativeGRGInputArea.lyr")
        input_area_features.value = input_layer_file_path

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
        # cell_units.filter.list = ['METERS', 'FEET']
        cell_units.filter.list = ['Meters', 'Feet']
        cell_units.value = cell_units.filter.list[0]

        label_start_position = arcpy.Parameter(name='label_start_position',
                                               displayName='Label Start Position',
                                               direction='Input',
                                               datatype='GPString',
                                               parameterType='Required',
                                               enabled=True,
                                               multiValue=False)
        label_start_position.filter.type = 'ValueList'
        # label_start_position.filter.list = ['UPPER_LEFT',
        #                                     'LOWER_LEFT',
        #                                     'UPPER_RIGHT',
        #                                     'LOWER_RIGHT']
        label_start_position.filter.list = ['Upper-Left',
                                            'Lower-Left',
                                            'Upper-Right',
                                            'Lower-Right']
        label_start_position.value = label_start_position.filter.list[0]

        label_type = arcpy.Parameter(name='label_type',
                                      displayName='Label Type',
                                      direction='Input',
                                      datatype='GPString',
                                      parameterType='Required',
                                      enabled=True,
                                      multiValue=False)
        label_type.filter.type = 'ValueList'
        # label_type.filter.list = ['ALPHA-NUMERIC',
        #                            'ALPHA-ALPHA',
        #                            'NUMERIC']
        label_type.filter.list = ['Alpha-Numeric',
                                   'Alpha-Alpha',
                                   'Numeric']
        label_type.value = label_type.filter.list[0]

        # TODO: define output schema as method
        output_features= arcpy.Parameter(name='output_grg_features',
                                         displayName='Output GRG Features',
                                         direction='Output',
                                         datatype='DEFeatureClass',
                                         parameterType='Required',
                                         enabled=True,
                                         multiValue=False)
        output_features.value = r"%scratchGDB%/area_grg"
        output_features.symbology = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                 "layers", "GRG.lyr")

        return [input_area_features,
                cell_width,
                cell_height,
                cell_units,
                label_start_position,
                label_type,
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

        input_start_location = arcpy.Parameter(name='input_start_location',
                                               displayName='Input Start Location',
                                               direction='Input',
                                               datatype='GPFeatureRecordSetLayer',
                                               parameterType='Required',
                                               enabled=True,
                                               multiValue=False)

        input_layer_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                             "layers",
                                             "RelativeGRGInputPoint.lyr")
        input_start_location.value = input_layer_file_path

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
        cell_width.value = 250.0

        cell_height = arcpy.Parameter(name='cell_height',
                                      displayName='Cell Height',
                                      direction='Input',
                                      datatype='GPDouble',
                                      parameterType='Required',
                                      enabled=True,
                                      multiValue=False)
        cell_height.value = 250.0

        cell_units = arcpy.Parameter(name='cell_units',
                                     displayName='Cell Units',
                                     direction='Input',
                                     datatype='GPString',
                                     parameterType='Required',
                                     enabled=True,
                                     multiValue=False)
        cell_units.filter.type = 'ValueList'
        # cell_units.filter.list = ['METERS', 'FEET']
        cell_units.filter.list = ['Meters', 'Feet']
        cell_units.value = cell_units.filter.list[0]

        # TODO: Are we really ever expecting a user to 'draw' a cell size? Doesn't make sense.
        grid_size_feature_set = arcpy.Parameter(name='grid_size_feature_set',
                                                displayName='Grid Size',
                                                direction='Input',
                                                datatype='GPFeatureRecordSetLayer',
                                                parameterType='Optional',
                                                enabled=True,
                                                multiValue=False)
        grid_size_feature_set.value = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                   "layers",
                                                   "RelativeGRGInputArea.lyr")


        label_start_position = arcpy.Parameter(name='label_start_position',
                                               displayName='Labeling Start Position',
                                               direction='Input',
                                               datatype='GPString',
                                               parameterType='Required',
                                               enabled=True,
                                               multiValue=False)
        label_start_position.filter.type = 'ValueList'
        # label_start_position.filter.list = ['UPPER_LEFT',
        #                                     'LOWER_LEFT',
        #                                     'UPPER_RIGHT',
        #                                     'LOWER_RIGHT']
        label_start_position.filter.list = ['Upper-Left',
                                            'Lower-Left',
                                            'Upper-Right',
                                            'Lower-Right']
        label_start_position.value = label_start_position.filter.list[0]

        label_type = arcpy.Parameter(name='label_type',
                                      displayName='Labeling type',
                                      direction='Input',
                                      datatype='GPString',
                                      parameterType='Required',
                                      enabled=True,
                                      multiValue=False)
        label_type.filter.type = 'ValueList'
        # label_style.filter.list = ['ALPHA-NUMERIC',
        #                            'ALPHA-ALPHA',
        #                            'NUMERIC']
        label_type.filter.list = ['Alpha-Numeric',
                                   'Alpha-Alpha',
                                   'Numeric']
        label_type.value = label_type.filter.list[0]

        output_features= arcpy.Parameter(name='output_grg_features',
                                         displayName='Output GRG Features',
                                         direction='Output',
                                         datatype='DEFeatureClass',
                                         parameterType='Required',
                                         enabled=True,
                                         multiValue=False)
        output_features.value = r"%scratchGDB%/point_grg"
        output_features.symbology = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                 "layers", "GRG.lyr")

        return [input_start_location,
                horizontal_cells,
                vertical_cells,
                cell_width,
                cell_height,
                cell_units,
                grid_size_feature_set,
                label_start_position,
                label_type,
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

        out_grg = GRGUtilities.GRGFromPoint(parameters[0].value,
                                            parameters[1].value,
                                            parameters[2].value,
                                            parameters[3].value,
                                            parameters[4].value,
                                            parameters[5].value,
                                            parameters[6].value,
                                            parameters[7].value,
                                            parameters[8].value,
                                            parameters[9].value)
        return out_grg

class DefineReferenceGridFromArea(object):
    '''
    Build polygon features of MGRS or USNG grids.
    '''
    def __init__(self):
        ''' Define Reference Grid From Area constructor '''
        self.label = "Define Reference Grid from Area"
        self.description = "Create an MGRS or USNG grid from an selected location on the map."
        self.GRID_LIST = ['GRID_ZONE_DESIGNATOR',
                          '100000M_GRID',
                          '10000M_GRID',
                          '1000M_GRID',
                          '100M_GRID',
                          '10M_GRID']
        self.REF_GRID_TYPE = ["MGRS",
                              "USNG"]
        self.LARGE_GRID_OPTIONS = ["ALLOW_LARGE_GRIDS",
                                   "NO_LARGE_GRIDS"]

    def getParameterInfo(self):
        '''
        Define parameter definitions
        '''

        input_area_features = arcpy.Parameter(name='input_area_features',
                                              displayName='Input Grid Area',
                                              direction='Input',
                                              datatype='GPFeatureRecordSetLayer',
                                              parameterType='Required',
                                              enabled=True,
                                              multiValue=False)
        input_layer_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                             "layers",
                                             "RelativeGRGInputArea.lyr")
        input_area_features.value = input_layer_file_path

        input_reference_grid = arcpy.Parameter(name='input_reference_grid',
                                               displayName='Reference Grid',
                                               direction='Input',
                                               datatype='GPString',
                                               parameterType='Required',
                                               enabled=True,
                                               multiValue=False)
        input_reference_grid.filter.type = 'ValueList'
        input_reference_grid.filter.list = self.REF_GRID_TYPE
        input_reference_grid.value = input_reference_grid.filter.list[0]

        grid_square_size = arcpy.Parameter(name='grid_square_size',
                                           displayName='Grid Square Size',
                                           direction='Input',
                                           datatype='GPString',
                                           parameterType='Required',
                                           enabled=True,
                                           multiValue=False)
        grid_square_size.filter.type = 'ValueList'
        grid_square_size.filter.list = self.GRID_LIST
        grid_square_size.value = grid_square_size.filter.list[0]

        output_features= arcpy.Parameter(name='output_grid_features',
                                         displayName='Output Grid Features',
                                         direction='Output',
                                         datatype='DEFeatureClass',
                                         parameterType='Required',
                                         enabled=True,
                                         multiValue=False)
        output_features.value = r"%scratchGDB%/output_grid"
        output_features.symbology = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                 "layers", "GRG.lyr")

        large_grid_handling = arcpy.Parameter(name='large_grid_handling',
                                           displayName='Large Grid Handling',
                                           direction='Input',
                                           datatype='GPString',
                                           parameterType='Optional',
                                           enabled=True,
                                           multiValue=False)
        large_grid_handling.filter.type = 'ValueList'
        large_grid_handling.filter.list = self.LARGE_GRID_OPTIONS
        large_grid_handling.value = large_grid_handling.filter.list[0]

        # message_window = arcpy.Parameter(name='message_window',
        #                                  displayName='message_window',
        #                                  direction='Input',
        #                                  datatype='GPString',
        #                                  parameterType='Optional',
        #                                  enabled='True')

        return [input_area_features,
                input_reference_grid,
                grid_square_size,
                output_features,
                large_grid_handling]

    def updateParameters(self, parameters):
        '''
        Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed.
        '''
        # #           get extent area (m**2) of features
        # #           remove 10m if greater than 200,000.0
        # #           remove 100m if greater than 20,000,000.0
        # #           remove 1000m if greater than 2,000,000,000.0
        # #           remove 10000m if greater than 200,000,000,000.0
        # if (parameters[0].hasBeenValidated is False) or parameters[0].altered:
        #     extent_area = arcpy.Describe(parameters[0]).extent.polygon.area
        #     if   extent_area > 200000.0:
        #         parameters[2].filter.list = self.GRID_LIST[0:5]
        #     elif extent_area > 20000000.0:
        #         parameters[2].filter.list = self.GRID_LIST[0:4]
        #     elif extent_area > 2000000000.0:
        #         parameters[2].filter.list = self.GRID_LIST[0:3]
        #     elif extent_area > 200000000000.0:
        #         parameters[2].filter.list = self.GRID_LIST[0:2]
        #     else:
        #         parameters[2].filter.list = self.GRID_LIST

        # vlist = []
        # parameters[4].value = ''
        # if parameters[0].hasBeenValidated is False:
        #     vlist.append(0)
        # if parameters[1].hasBeenValidated is False:
        #     vlist.append(1)
        # if parameters[2].hasBeenValidated is False:
        #     vlist.append(2)
        # if parameters[3].hasBeenValidated is False:
        #     vlist.append(3)
        # vmsg = 'validated {}'.format(vlist)
        #
        # alist = []
        # if parameters[0].altered is True:
        #     alist.append(0)
        # if parameters[1].altered is True:
        #     alist.append(1)
        # if parameters[2].altered is True:
        #     alist.append(2)
        # if parameters[3].altered is True:
        #     alist.append(3)
        # amsg = 'altered {}'.format(alist)
        #
        # parameters[4].value = '{}, {}'.format(vmsg, amsg)

        return

    def updateMessages(self, parameters):
        '''
        Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation
        '''
        return

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def execute(self, parameters, messages):
        ''' execute for toolbox'''

        RG = RefGrid.ReferenceGrid(parameters[0].value,
                                   parameters[1].value,
                                   parameters[2].value,
                                   parameters[4].value)
        out_grid = RG.Build(parameters[3].value)
        return out_grid


def _outputGRGSchema():
    ''' '''
    # TODO: implement output schema for all GRG features
    # * has Grid field (name: Grid, Alias: Grid, data type: Text, Length: 255)
    # * Polygon feature class,
    # * Coordinate system: <Undefined> AAAAAAAAHHHHHHH!!!!!!
    # *
    return None

