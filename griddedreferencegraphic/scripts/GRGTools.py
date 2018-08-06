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
 requirements: ArcGIS 10.3.1+, ArcGIS Pro 1.4+, Python 2.7 or Python 3.5+
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
    from . import Utilities
    from . import GRGUtilities
    from . import RefGrid
except ImportError:
    import Utilities
    import GRGUtilities
    import RefGrid

class CreateGRGFromArea(object):
    '''
    Create a Gridded Reference Graphic (GRG) from an selected area on the map.
    '''
    def __init__(self):
        '''
        Create GRG From Area tool constructor method
        '''
        self.label = "Create GRG From Area"
        self.description = "Create a Gridded Reference Graphic (GRG) from an selected area on the map."
        self.category = "Gridded Reference Graphic"

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
        cell_units.filter.list = ['Meters', 'Feet','Miles','Kilometers','Nautical Miles','Yards']
        cell_units.value = cell_units.filter.list[0]

        label_start_position = arcpy.Parameter(name='label_start_position',
                                               displayName='Start Position',
                                               direction='Input',
                                               datatype='GPString',
                                               parameterType='Required',
                                               category='Label Properties',
                                               enabled=True,
                                               multiValue=False)
        label_start_position.filter.type = 'ValueList'
        label_start_position.filter.list = ['Upper-Left',
                                            'Lower-Left',
                                            'Upper-Right',
                                            'Lower-Right']
        label_start_position.value = label_start_position.filter.list[0]

        label_type = arcpy.Parameter(name='label_type',
                                      displayName='Type',
                                      direction='Input',
                                      datatype='GPString',
                                      parameterType='Required',
                                      category='Label Properties',
                                      enabled=True,
                                      multiValue=False)
        label_type.filter.type = 'ValueList'
        label_type.filter.list = ['Alpha-Numeric',
                                   'Alpha-Alpha',
                                   'Numeric']
        label_type.value = label_type.filter.list[0]

        label_seperator = arcpy.Parameter(name='label_seperator',
                                      displayName='Separator (Only used for Alpha-Alpha labeling)',
                                      direction='Input',
                                      datatype='GPString',
                                      parameterType='Required',
                                      category='Label Properties',
                                      enabled=False,
                                      multiValue=False)
        label_seperator.filter.type = 'ValueList'
        label_seperator.filter.list = ['-',',','.','/']
        label_seperator.value = label_seperator.filter.list[0]

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
                label_seperator,
                output_features]

    def updateParameters(self, parameters):
        '''
        Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed.
        '''
        if parameters[5].value == "Alpha-Alpha":
          parameters[6].enabled = True
        else:
          parameters[6].enabled = False
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
                                           parameters[6].value,
                                           parameters[7].value)
        return out_grg

class CreateGRGFromPoint(object):
    '''
    Create a Gridded Reference Graphic (GRG) from an selected location on the map.
    '''
    def __init__(self):
        ''' Point Target GRG constructor '''
        self.label = "Create GRG From Point"
        self.description = "Create a Gridded Reference Graphic (GRG) from an selected location on the map."
        self.category = "Gridded Reference Graphic"

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
                                           displayName='Number of Rows',
                                           direction='Input',
                                           datatype='GPDouble',
                                           parameterType='Required',
                                           enabled=True,
                                           multiValue=False)
        horizontal_cells.value = 10

        vertical_cells = arcpy.Parameter(name='vertical_cells',
                                         displayName='Number of Columns',
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
        cell_units.filter.list = ['Meters', 'Feet','Miles','Kilometers','Nautical Miles','Yards']
        cell_units.value = cell_units.filter.list[0]

        label_start_position = arcpy.Parameter(name='label_start_position',
                                               displayName='Start Position',
                                               direction='Input',
                                               datatype='GPString',
                                               parameterType='Required',
                                               category='Label Properties',
                                               enabled=True,
                                               multiValue=False)
        label_start_position.filter.type = 'ValueList'
        label_start_position.filter.list = ['Upper-Left',
                                            'Lower-Left',
                                            'Upper-Right',
                                            'Lower-Right']
        label_start_position.value = label_start_position.filter.list[0]

        label_type = arcpy.Parameter(name='label_type',
                                      displayName='Type',
                                      direction='Input',
                                      datatype='GPString',
                                      parameterType='Required',
                                      category='Label Properties',
                                      enabled=True,
                                      multiValue=False)
        label_type.filter.type = 'ValueList'
        label_type.filter.list = ['Alpha-Numeric',
                                   'Alpha-Alpha',
                                   'Numeric']
        label_type.value = label_type.filter.list[0]

        label_seperator = arcpy.Parameter(name='label_seperator',
                                      displayName='Separator (Only used for Alpha-Alpha labeling)',
                                      direction='Input',
                                      datatype='GPString',
                                      parameterType='Required',
                                      category='Label Properties',
                                      enabled=False,
                                      multiValue=False)
        label_seperator.filter.type = 'ValueList'
        label_seperator.filter.list = ['-',',','.','/']
        label_seperator.value = label_seperator.filter.list[0]

        grid_angle = arcpy.Parameter(name='grid_angle',
                                      displayName='Grid Rotation',
                                      direction='Input',
                                      datatype='GPLong',
                                      parameterType='Required',
                                      enabled=True,
                                      multiValue=False)
        grid_angle.value = 0

        output_features= arcpy.Parameter(name='output_grg_features',
                                         displayName='Output GRG Features',
                                         direction='Output',
                                         datatype=u'Feature Class',
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
                label_start_position,
                label_type,
                label_seperator,
                grid_angle,
                output_features]

    def updateParameters(self, parameters):
        '''
        Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed.
        '''
        if parameters[7].value == "Alpha-Alpha":
          parameters[8].enabled = True
        else:
          parameters[8].enabled = False

        return

    def updateMessages(self, parameters):
        '''
        '''
        if parameters[9].value < -89 or parameters[9].value > 89:
          parameters[9].setErrorMessage("Grid angle must be between -89 and 89")
        return

    def execute(self, parameters, messages):
        ''' execute for toolbox'''

        pointTargets = parameters[0].value #Input Location(s)
        rows         = parameters[1].value #Number Horizontal Cells
        cols         = parameters[2].value #Number Vertical Cells
        cellWidth    = parameters[3].value #Cell Width
        cellHeight   = parameters[4].value #Cell Height
        cellUnits    = parameters[5].value #Cell Units
        labelStart   = parameters[6].value #Labeling Start Postiton
        labelStyle   = parameters[7].value #Labeling Type
        labelSeparator    = parameters[8].value #Labeling Seperator
        gridRotationAngle = parameters[9].value #Grid Angle
        output            = parameters[10].valueAsText  #Output

        out_grg = GRGUtilities.GRGFromPoint(pointTargets, \
                rows, cols, \
                cellWidth, cellHeight, cellUnits, \
                labelStart, labelStyle, labelSeparator, gridRotationAngle, \
                output)

        return out_grg

class CreateReferenceSystemGRGFromArea(object):
    '''
    Build polygon features of MGRS or USNG gridded reference graphics.
    '''
    def __init__(self):
        ''' Define Reference Grid From Area constructor '''
        self.label = "Create Reference System GRG From Area"
        self.description = "Create an MGRS or USNG gridded reference graphic from an selected area on the map."
        self.category = "Gridded Reference Graphic"
        self.GRID_LIST = ['GRID_ZONE_DESIGNATOR',
                          '100000M_GRID',
                          '10000M_GRID',
                          '1000M_GRID',
                          '100M_GRID',
                          '10M_GRID']
        self.REF_GRID_TYPE = ["MGRS",
                              "USNG"]
        self.LARGE_GRID_OPTIONS = ["NO_LARGE_GRIDS",
                                   "ALLOW_LARGE_GRIDS"]

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

        input_grid_reference_system = arcpy.Parameter(name='input_grid_reference_system',
                                               displayName='Grid Reference System',
                                               direction='Input',
                                               datatype='GPString',
                                               parameterType='Required',
                                               enabled=True,
                                               multiValue=False)
        input_grid_reference_system.filter.type = 'ValueList'
        input_grid_reference_system.filter.list = self.REF_GRID_TYPE
        input_grid_reference_system.value = input_grid_reference_system.filter.list[0]

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

        output_grid_features= arcpy.Parameter(name='output_grid_features',
                                         displayName='Output GRG Features',
                                         direction='Output',
                                         datatype='DEFeatureClass',
                                         parameterType='Required',
                                         enabled=True,
                                         multiValue=False)
        output_grid_features.value = r"%scratchGDB%/output_grid"
        output_grid_features.symbology = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                 "layers", "OutputRefGrid.lyr")

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

        return [input_area_features,
                input_grid_reference_system,
                grid_square_size,
                output_grid_features,
                large_grid_handling]

    def updateParameters(self, parameters):
        '''
        Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed.
        '''

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

class NumberFeatures(object):
    '''
    Number input features within a specified area.
    '''
    def __init__(self):
        '''
        Number Features constructor
        '''
        self.label = "Number Features"
        self.description = "Number input point features within a selected area."
        self.category = "Gridded Reference Graphic"

    def getParameterInfo(self):
        '''
        Define parameter definitions
        '''
        input_area_features = arcpy.Parameter(name='input_area_features',
                                              displayName='Input Area to Number',
                                              direction='Input',
                                              datatype='GPFeatureRecordSetLayer',
                                              parameterType='Required',
                                              enabled=True,
                                              multiValue=False)
        input_layer_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                             "layers",
                                             "RelativeNumberFeaturesAreaInput.lyr")
        input_area_features.value = input_layer_file_path

        input_number_features = arcpy.Parameter(name='input_point_features',
                                               displayName='Features to Number',
                                               direction='Input',
                                               datatype='GPFeatureLayer',
                                               parameterType='Required',
                                               enabled=True,
                                               multiValue=False)

        field_to_number = arcpy.Parameter(name='field_to_number',
                                          displayName='Field to Number',
                                          direction='Input',
                                          datatype='Field',
                                          parameterType='Optional',
                                          enabled=True,
                                          multiValue=False)
        field_to_number.filter.list = ['Short', 'Long', 'Double', 'Single']
        field_to_number.parameterDependencies = [input_number_features.name]

        output_features= arcpy.Parameter(name='output_features',
                                         displayName='Output Numbered Features',
                                         direction='Output',
                                         datatype='DEFeatureClass',
                                         parameterType='Optional',
                                         enabled=True,
                                         multiValue=False)
        app = Utilities.GetPlatform()
        layerFile = "NumberedFeatures.lyrx"

        if (app == 'ARCMAP'):
			# Layerfile for ArcMap
            layerFile = "NumberedFeatures.lyr"

        output_features.symbology = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                                 "layers", layerFile)

        return [input_area_features,
                input_number_features,
                field_to_number,
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
        Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation
        '''
        return

    def execute(self, parameters, messages):
        ''' execute the tool'''

        arcpy.env.overwriteOutput = True

        areaToNumber   = parameters[0].value
        pointFeatures  = parameters[1].value
        numberingField = parameters[2].value
        outputFeatureClass = parameters[3].value

        output_fc = GRGUtilities.NumberFeatures(areaToNumber,
                        pointFeatures,
                        numberingField,
                        outputFeatureClass)

        return output_fc

def _outputGRGSchema():
    ''' '''
    # TODO: implement output schema for all GRG features
    # * has Grid field (name: Grid, Alias: Grid, data type: Text, Length: 255)
    # * Polygon feature class,
    # * Coordinate system: <Undefined> AAAAAAAAHHHHHHH!!!!!!
    # *
    return None

