# -*- coding: utf-8 -*-
import arcpy
import collections
import mds
import mds.messages
import numpy
import numpy.lib.recfunctions
import os
import tempfile

#
# LIMITATIONS:
#   > Chaining in ModelBuilder:
#   Because we test whether an Input File or URL String dataset is valid by
#   attempting to open the dataset, this parameter is not able to be chained
#   in ModelBuilder.
#
#   > Environment variables:
#   This script tool makes use of the geoprocessing tools 'Feature to Raster',
#   'Lookup', 'Resample', and 'Raster to Polygon', which are variously affected
#   by environment settings, such as Extent, Snap Raster, and NoData.  Altering
#   these environment variables from their defaults may have deleterious effects
#   on the execution of this script tool.
#
#   > Memory:
#   Because of the combinatorial nature of this tool and the generation of the
#   entire table in memory prior to outputting it with NumPyArrayToTable,
#   memory could become an issue.
#
#   > Discrete Geometries:
#   For discrete datasets, the tool has been designed to read CF 1.6 discrete
#   sampling geometry compliant datasets that are of a 'point', 'timeseries', or
#   'profile' feature type and use an orthogonal or incomplete multidimensional
#   array data representation.  Other types and data representations are not
#   supported.
#
#   > Zone alignment:
#   For a gridded netCDF variable, based on the order of the x and y dimensions
#   of the netCDF data and whether the values are ascending or descending, we
#   flip and rotate the zone data to match the netCDF data.  If this is
#   unsuccessful, the output netCDF file may have no data in it or mismatch
#   with the Input Zone Data.
#
#   > Data extents:
#   For a gridded netCDF variable, we extract the zone data from the raster
#   zone dataset (possibly after conversion from feature) based on the extent
#   of the coordinate dimensions of the gridded variable.  If the zone data
#   extent does not overlap the extent of the coordinate dimensions, we throw a
#   warning. However, in the case that the zone data uses a GCS coordinate
#   system (which should match that of the gridded variable), we first try
#   converting the gridded variable's extent to the ranges lon[-180, 180] and
#   lat[-90, 90].  Consequently, if the output netCDF file has no data in it
#   or mismatches with the Input Zone Data, an extent mismatch may be the reason.
#   In such a case, the zone data must be altered to align with the gridded
#   data.  Note that we apply the range conversion to try to solve the problem
#   for input datasets using, for example, a longitude variable in the range
#   [220, 300], as might be done to depict the USA.
#
class MultidimensionalZonalStatisticsAsTable(object):
    def __init__(self):
        """Defines the tool."""
        self.label = "Multidimensional Zonal Statistics as Table"
        self.description = "Calculates zonal statistics over non-surface " + \
        "dimensions for a variable in a multidimensional dataset, such as " + \
        "netCDF or HDF, or other dataset accessible through the OPeNDAP " + \
        "protocol, and outputs the result as a table."
        self.canRunInBackground = False
        # Statistics options
        statistics_numpy = {'MAXIMUM':'max', \
                               'MEAN':'mean', \
                            'MINIMUM':'min', \
                              'RANGE':'ptp', \
                                'STD':'std', \
                                'SUM':'sum', \
                           'VARIANCE':'var'}
        statistics_numpycateg = {'MEDIAN':'median'}
        statistics_categorical = {'MAJORITY':'majority', \
                                  'MINORITY':'minority', \
                                   'VARIETY':'variety'}
        statistics_multiple = {'ALL_FLOAT':'multistats', \
                                'MIN_MAX':'multistats', \
                               'MEAN_STD':'multistats', \
                           'MIN_MAX_MEAN':'multistats'}
        statistics_multiple_cat = {'ALL':'multistats'}
        # Look up of individual statistics for 'multistats' function
        self.statistics_multiple_values = {'ALL':['MAXIMUM','MEAN','MINIMUM', \
               'RANGE','STD','SUM','VARIANCE','MEDIAN','MAJORITY','MINORITY', \
                                                                  'VARIETY'], \
                                     'ALL_FLOAT':['MAXIMUM','MEAN','MINIMUM', \
                                             'RANGE','STD','SUM','VARIANCE'], \
                                       'MIN_MAX':['MINIMUM','MAXIMUM'], \
                                      'MEAN_STD':['MEAN','STD'], \
                                  'MIN_MAX_MEAN':['MINIMUM','MAXIMUM','MEAN']}
        # List of dictionaries of statistics
        # Sublist elements indices:
        #   0: object
        #   1: dictionary defined by 'displayname':'methodname'
        #       where object.methodname() is valid and displayname is what is
        #       shown to the user
        #   2: boolean, indicating whether the given dictionary of statistics
        #       only operates on integer datatypes
        self.statistics = [[numpy.ma, statistics_numpy, False], \
                           [self, statistics_categorical, True], \
                           [numpy.ma, statistics_numpycateg, True], \
                           [self, statistics_multiple, False], \
                           [self, statistics_multiple_cat, True]]
        self.default_statistic = 'ALL_FLOAT'

    # ---------------------------------------------------------
    # Statistics

    def majority(self, var1):
        """Calculates majority for given NumPy array.  The lowest value
        is return in the case of ties."""
        vunique = numpy.ma.compressed(numpy.unique(var1))
        vcounts = numpy.zeros_like(vunique)
        for vindex in range(0, vunique.size):
            vcounts[vindex] = numpy.ma.sum(var1 == vunique[vindex])
        return vunique[numpy.argmax(vcounts)]

    def minority(self, var1):
        """Calculates minority for given NumPy array.  The lowest value
        is return in the case of ties."""
        vunique = numpy.ma.compressed(numpy.unique(var1))
        vcounts = numpy.zeros_like(vunique)
        for vindex in range(0, vunique.size):
            vcounts[vindex] = numpy.ma.sum(var1 == vunique[vindex])
        return vunique[numpy.argmax(vcounts)]

    def variety(self, var1):
        """Calculates variety for a given NumPy array."""
        return numpy.ma.compressed(numpy.unique(var1)).size

    def multistats(self, var1, statistic):
        """Create structured array and save values for multiple statistics"""
        stat_dtype = [(stat, numpy.float) for stat in \
            self.statistics_multiple_values[statistic]]
        result = numpy.zeros(1, numpy.dtype(stat_dtype))
        for stat in self.statistics_multiple_values[statistic]:
            result[stat] = (self.calculate_statistic(var1, stat))
        return result

    def calculate_statistic(self, variable, statistic):
        """Calculates given statistic for a NumPy array based on look-up
        in self.statistics."""
        # Get statistic function
        for stat in self.statistics:
            if statistic in stat[1]:
                func = getattr(stat[0], stat[1][statistic])
                break
        else:
            # Default
            statistic = 'ALL_FLOAT'
            func = getattr(self, 'multistats')
        # Apply statistic function
        if statistic in self.statistics_multiple_values:
            # Multivalued case
            return func(variable, statistic)
        else:
            # Single valued case
            return func(variable)

    # ---------------------------------------------------------

    def getParameterInfo(self):
        """Defines parameter definitions"""

        parameters = []

        # Input zone parameter
        parameters.append(arcpy.Parameter(
            displayName="Input Raster or Feature Zone Data",
            name="in_zone_data",
            datatype=["GPRasterLayer","GPFeatureLayer"],
            parameterType="Required",
            direction="Input"))

        # Input netCDF parameter
        parameters.append(arcpy.Parameter(
            displayName="Input Value File or URL String",
            name="in_value_file",
            datatype=["DEFile","GPString"],
            parameterType="Required",
            direction="Input"))

        # Variable parameter
        parameters.append(arcpy.Parameter(
            displayName="Variable",
            name="variable",
            datatype="GPString",
            parameterType="Required",
            direction="Input"))

        parameters[-1].parameterDependencies = [parameters[-2].name]

        # Output Table parameter
        parameters.append(arcpy.Parameter(
            displayName="Output Table",
            name="out_table",
            datatype="DEFile",
            parameterType="Required",
            direction="Output"))

        # Type parameter
        parameters.append(arcpy.Parameter(
            displayName="Statistic Type",
            name="statistic_type",
            datatype="GPString",
            parameterType="Optional",
            direction="Input"))

        parameters[-1].filter.type = "ValueList"
        parameters[-1].filter.list = sorted([key for stat in \
            self.statistics for key in stat[1].keys()])
        parameters[-1].value = self.default_statistic

        # Ignore parameter
        parameters.append(arcpy.Parameter(
            displayName="Ignore NoData in Calculations",
            name="ignore_nodata",
            datatype="GPBoolean",
            parameterType="Optional",
            direction="Input"))

        parameters[-1].filter.list = ['IGNORE','NO_IGNORE']
        parameters[-1].value = 'IGNORE'

        # Input zone field
        parameters.append(arcpy.Parameter(
            displayName="Zone Field",
            name="zone_field",
            datatype="GPString",
            parameterType="Optional",
            direction="Input"))

        parameters[-1].parameterDependencies = [parameters[-7].name]

        return parameters

    def isLicensed(self):
        """Execute only if the ArcGIS Spatial Analyst extension is available."""
        try:
            if arcpy.CheckExtension("Spatial") == "Available":
                #arcpy.CheckOutExtension("Spatial")
                return True
            else:
                return False
        except:
            return False # tool cannot be executed
        return True # tool can be executed

    def updateParameters(self, parameters):
        """Modifies the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        zone_parameter = parameters[0]
        input_parameter = parameters[1]
        variable_parameter = parameters[2]
        output_parameter = parameters[3]
        type_parameter = parameters[4]
        ignore_parameter = parameters[5]
        zonefield_parameter = parameters[6]

        # Populate the output netCDF file parameter with a reasonable default
        # (i.e. the name of the variable with 'zonal_' appended to it.)
        if (variable_parameter.value is not None) and (not output_parameter.altered):
            out_file_name = variable_parameter.valueAsText + '_zonal'
            # Generate a unique name
            i = 1
            temp_name = out_file_name + '.dbf'
            while arcpy.Exists(temp_name):
                temp_name = out_file_name + str(i) + '.dbf'
                i += 1
            out_file_name = temp_name
            workspace = arcpy.env.workspace
            output_parameter.value = os.path.join(workspace, out_file_name)

        # Set zone parameter default
        if (zone_parameter.value is not None) and (not zonefield_parameter.altered):
            valid_raster_types = ["RasterLayer", "RasterDataset"]
            valid_feature_types = ["ShapeFile","FeatureLayer", "FeatureDataset"]
            desc = arcpy.Describe(zone_parameter.value)
            if desc.dataType in valid_raster_types:
                zonefield_parameter.value = "Value"
            else:
                zonefield_parameter.value = "FID"

        return

    def updateMessages(self, parameters):
        """Modifies the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        zone_parameter = parameters[0]
        input_parameter = parameters[1]
        variable_parameter = parameters[2]
        output_parameter = parameters[3]
        type_parameter = parameters[4]
        ignore_parameter = parameters[5]
        zonefield_parameter = parameters[6]
        dataset = None

        if zone_parameter.value is not None:
            valid_raster_types = ["RasterLayer", "RasterDataset"]
            valid_feature_types = ["ShapeFile","FeatureLayer", "FeatureDataset"]
            desc = arcpy.Describe(zone_parameter.value)
            if desc.dataType in valid_raster_types:
                # Check that raster is of an integer data type
                if not hasattr(desc, 'isInteger') or not desc.isInteger:
                    zone_parameter.setErrorMessage(
                        mds.messages.ZONE_RASTER_NOT_INTEGER.format(
                            zone_parameter.valueAsText))
                else:
                    # Fill zone field parameter for raster
                    if hasattr(desc, 'fields'):
                        zonefield_parameter.filter.type = "ValueList"
                        validtypes = ['Integer','SmallInteger','String']
                        zonefield_parameter.filter.list = [zonefield.name for \
                            zonefield in desc.fields if zonefield.type in validtypes]
                    else:
                        zonefield_parameter.filter.type = "ValueList"
                        zonefield_parameter.filter.list = ['Value']
            elif desc.dataType in valid_feature_types:
                # Fill zone field parameter for feature class
                zonefield_parameter.filter.type = "ValueList"
                validtypes = ['OID','Integer','SmallInteger','String']
                zonefield_parameter.filter.list = [zonefield.name for \
                    zonefield in desc.fields if zonefield.type in validtypes]
            else:
                zonefield_parameter.filter.type = "ValueList"
                zonefield_parameter.filter.list = []
        else:
            # Clear zone field list if no zone dataset specified
            zonefield_parameter.filter.type = "ValueList"
            zonefield_parameter.filter.list = []

        # Open netCDF dataset
        if input_parameter.value is not None:
            try:
                dataset = mds.netcdf.Dataset(input_parameter.valueAsText, '')
            except RuntimeError, exception:
                if "No such file or directory" in str(exception) or \
                    "Invalid argument" in str(exception):
                    input_parameter.setErrorMessage(
                        mds.messages.INPUT_FILE_DOES_NOT_EXIST.format(
                            input_parameter.valueAsText))
                elif "Malformed or inaccessible DAP DDS" in str(exception):
                    input_parameter.setErrorMessage(
                        mds.messages.INPUT_DATASET_URL_MALFORMED.format(
                            input_parameter.valueAsText))
                else:
                    input_parameter.setErrorMessage(
                        mds.messages.INPUT_DATASET_GENERIC_ERROR.format(
                            input_parameter.valueAsText, str(exception)))
            except Exception, exception:
                input_parameter.setErrorMessage(
                    mds.messages.INPUT_DATASET_GENERIC_ERROR.format(
                        input_parameter.valueAsText, str(exception)))
            if dataset is not None:
                # Try to fill variable list with spatial variables
                var_list = list(dataset.spatial_data_variable_names())
                if var_list != []:
                    # If successful, we likely have a gridded dataset.  We
                    # will check regular gridding on execution.
                    variable_parameter.filter.type = "ValueList"
                    variable_parameter.filter.list = var_list
                else:
                    # If unsuccessful, try to fill variable list assuming
                    # dataset is of a discrete geometry type.
                    var_list = list(dataset.data_variable_names())
                    var_filter = []
                    for var_item in var_list:
                        var_stat, var_x, var_y = self.get_dependent_variables(
                            dataset, var_item)
                        if (var_stat is not None) and (var_x is not None) and (
                            var_y is not None):
                            var_filter = self.get_variables_by_dimension(
                                dataset, var_stat)
                            break
                    variable_parameter.filter.type = "ValueList"
                    variable_parameter.filter.list = var_filter
        else:
            # Clear variable list if no input dataset specified
            variable_parameter.filter.type = "ValueList"
            variable_parameter.filter.list = []
            variable_parameter.value = ""

        # Modify statistic choices so that, if any variable is not of integer
        # type, categorical statistics are not offered.
        if variable_parameter.value is not None:
            if (dataset is not None) and (variable_parameter.value in \
                dataset.variable_names()):
                var = dataset.variable(variable_parameter.value)
                ispacked = hasattr(var,'scale_factor') or hasattr(var, 'add_offset')
                flag = ('int' in str(var.dtype)) and not ispacked
                type_parameter.filter.list = sorted([key for stat in \
                    self.statistics if flag or not stat[2] for key in \
                    stat[1].keys()])
        else:
            # When variable parameter is cleared, make all statistics available
            type_parameter.filter.list = sorted([key for stat in \
            self.statistics for key in stat[1].keys()])

        # Ensure output table has a .dbf extension
        if output_parameter.value is not None:
            output_filename = output_parameter.valueAsText
            if os.path.splitext(output_filename)[1] != ".dbf":
                output_parameter.setErrorMessage(
                    mds.messages.OUTPUT_FILE_EXTENSION_MUST_BE_DBF)

        return


    def execute(self, parameters, messages):
        """The source code of the tool."""

        zone_parameter = parameters[0]
        input_parameter = parameters[1]
        variable_parameter = parameters[2]
        output_parameter = parameters[3]
        type_parameter = parameters[4]
        ignore_parameter = parameters[5]
        zonefield_parameter = parameters[6]

        # Grab the parameter values
        dataset_name = input_parameter.valueAsText      # input netCDF filename
        output_filename = output_parameter.valueAsText  # output filename
        var_name = variable_parameter.valueAsText       # netCDF variable name

        # Try to open the netCDF dataset
        try:
            dataset = mds.netcdf.Dataset(dataset_name,'')
        except RuntimeError, exception:
            messages.addErrorMessage(str(exception))
            raise arcpy.ExecuteError

        # Based on same criteria used to populate variable_parameter in
        #   updateMessages(), check if input dataset is gridded or contains
        #   discrete geometries and branch code appropriately.
        if list(dataset.spatial_data_variable_names()) != []:
            self.zonal_statistics_as_table_for_grid(parameters, messages, dataset)
        else:
            self.zonal_statistics_as_table_for_discrete(parameters, messages, dataset)

        return

    def zonal_statistics_as_table_for_grid(self, parameters, messages, dataset):
        """Performs zonal statistics as table assuming dataset contains
        regularly gridded variables."""

        zone_parameter = parameters[0]
        input_parameter = parameters[1]
        variable_parameter = parameters[2]
        output_parameter = parameters[3]
        type_parameter = parameters[4]
        ignore_parameter = parameters[5]
        zonefield_parameter = parameters[6]

        # Grab the parameter values
        dataset_name = input_parameter.valueAsText      # input netCDF filename
        output_filename = output_parameter.valueAsText  # output filename
        var_name = variable_parameter.valueAsText       # netCDF variable name

        # Extract variable from netCDF dataset
        arr_var = dataset.variable(var_name)

        # Check that spatial dimensions of input netCDF variable are regularly
        #   gridded and obtain cell size
        cell_size_x = None
        cell_size_y = None
        spat_list = list(dataset.space_dimension_names(var_name))
        assert len(spat_list) >= 2
        spat_var = dataset.variable(spat_list[0])
        blfirst = True
        if spat_var.size > 1:
            for i in range(spat_var.size - 1):
                cell_size_x = spat_var[i+1] - spat_var[i]
                if (not blfirst) and (cell_size_x != last_cell_size):
                    messages.addErrorMessage(
                        mds.messages.VARIABLE_NOT_REGULARLY_GRIDDED.format(
                            var_name, spat_list[0]))
                    raise arcpy.ExecuteError
                    break
                last_cell_size = cell_size_x
                blfirst = False
            cell_size_x = float(cell_size_x)
        spat_var = dataset.variable(spat_list[1])
        blfirst = True
        if spat_var.size > 1:
            for i in range(spat_var.size - 1):
                cell_size_y = spat_var[i+1] - spat_var[i]
                if (not blfirst) and (cell_size_y != last_cell_size):
                    messages.addErrorMessage(
                        mds.messages.VARIABLE_NOT_REGULARLY_GRIDDED.format(
                            var_name, spat_list[1]))
                    raise arcpy.ExecuteError
                    break
                last_cell_size = cell_size_y
                blfirst = False
            cell_size_y = float(cell_size_y)
        # If both x and y cell sizes are None, the dataset is a scalar.
        if (cell_size_x is None) and (cell_size_y is None):
            messages.addErrorMessage(
                mds.messages.VARIABLE_CONTAINS_INSUFFICIENT_VALUES.format(
                    var_name))
            raise arcpy.ExecuteError
        # If one of x and y is None, the dataset is a line, so we will assume
        #   the singleton dimension shares the other's cell size.
        if cell_size_x is None:
            cell_size_x = cell_size_y
            messages.addWarningMessage(
                ("Assuming variable dimension {} shares a cell size of {} " + \
                "with {}").format(spat_list[0], cell_size_y, spat_list[1]))
        if cell_size_y is None:
            cell_size_y = cell_size_x
            messages.addWarningMessage(
                ("Assuming variable dimension {} shares a cell size of {} " + \
                "with {}").format(spat_list[1], cell_size_x, spat_list[0]))

        # Figure out which spatial variable is x and which is y
        #   and then get corresponding number of columns and rows
        if dataset.convention.is_x_dimension_variable(dataset.variable(spat_list[0])):
            ncol = len(dataset.variable(spat_list[0]))
            nrow = len(dataset.variable(spat_list[1]))
            bltranspose = True
        else:
            ncol = len(dataset.variable(spat_list[1]))
            nrow = len(dataset.variable(spat_list[0]))
            cell_size_x, cell_size_y = cell_size_y, cell_size_x
            bltranspose = False

        # Grab extent from netCDF dataset
        #   i.e. [x_min, y_min, x_max, y_max]
        var_extent = dataset.extent(var_name)
        # Lower left hand corner of netCDF variable spatial slice
        xl = float(var_extent[0])
        yl = float(var_extent[1])

        # Determine whether to flip the zone data over a given axis and
        #   transpose it to align with the netCDF data
        blflipx = False
        blflipy = False
        if cell_size_y > 0:
            blflipx = True
        if cell_size_x < 0:
            blflipy = True

        # Use absolute cell sizes
        cell_size_x = abs(cell_size_x)
        cell_size_y = abs(cell_size_y)

        # Convert extent to extent object for use later
        var_extent = arcpy.Extent(var_extent[0], var_extent[1], \
            var_extent[2], var_extent[3])

        # Was a temporary raster created?
        bltempRaster = False

        # Describe zone data
        desc = arcpy.Describe(zone_parameter.value)

        # Environments
        arcpy.env.outputCoordinateSystem = desc.spatialReference
        temp_snap = arcpy.NumPyArrayToRaster(numpy.zeros((1,1)), \
            arcpy.Point(xl,yl), cell_size_x, cell_size_y)
        arcpy.env.snapRaster = temp_snap

        # Process input zone data
        valid_raster_types = ["RasterLayer", "RasterDataset"]
        valid_feature_types = ["ShapeFile","FeatureLayer", "FeatureDataset"]
        if desc.dataType in valid_feature_types:
            # Limitation of Feature to Raster
            if cell_size_x != cell_size_y:
                messages.addErrorMessage(
                    "The variable %s must use the same gridding " + \
                    "for both its spatial dimensions when feature zone " + \
                    "data is used." % var_name)
                raise arcpy.ExecuteError
            # Convert features
            temp_raster = 'in_memory\\temp'
            arcpy.FeatureToRaster_conversion(zone_parameter.value, \
                zonefield_parameter.value, temp_raster, cell_size_x)
            bltempRaster = True
            # NoData value
            noDataValue = arcpy.Describe(temp_raster).noDataValue
        elif desc.dataType in valid_raster_types:
            # Map non-Value field to Value if necessary and grab NoData value
            if zonefield_parameter.value != 'Value':
                in_raster = arcpy.sa.Lookup(zone_parameter.value, \
                    zonefield_parameter.value)
                # Raster created with Lookup will have default noDataValue
                # used for given .pixelType, but not assigned to .noDataValue
                if '8' in in_raster.pixelType:
                    noDataValue = -128  # S8
                else:
                    noDataValue = -2147483647 # S32
            else:
                in_raster = zone_parameter.valueAsText
                noDataValue = desc.noDataValue
            # Resample if necessary
            if (desc.meanCellHeight != cell_size_y) or \
                (desc.meanCellWidth != cell_size_x):
                temp_raster = 'in_memory\\temp'
                arcpy.Resample_management(in_raster, temp_raster, \
                    "%f %f" % (cell_size_x, cell_size_y))
                bltempRaster = True
            else:
                temp_raster = in_raster
        else:
            messages.addErrorMessage("Not a valid zone dataset.")
            raise arcpy.ExecuteError

        # Make raster object from zone data if not already
        if not isinstance(temp_raster, arcpy.Raster):
            temp_raster = arcpy.Raster(temp_raster)

        # Limit to lon [-180, 180] and lat [-90, 90]
        def convert_coord(num, islon = True):
            lim = 180 if islon else 90
            if num > lim:
                out = num % -lim
            elif num < -lim:
                out = num % lim
            else:
                out = num
            if not islon:
                mult = -1.0 if num < 0 else 1.0
                out = mult * abs(out)
            return out

        # Determine whether input zone data has a PCS or GCS
        if (temp_raster.spatialReference.exporttostring() == \
                temp_raster.spatialReference.GCS.exporttostring()):
            # Test for overlap between zone and netCDF data
            if temp_raster.extent.disjoint(var_extent):
                # Try with coordinates in lon[-180,180] and lat[-90,90] ranges
                var_extent_temp = arcpy.Extent(
                    convert_coord(var_extent.XMin, True),
                    convert_coord(var_extent.YMin, True),
                    convert_coord(var_extent.XMax, False),
                    convert_coord(var_extent.YMax, False))
                xl = var_extent_temp.XMin
                yl = var_extent_temp.YMin
                # Check again and throw warning on failure
                if temp_raster.extent.disjoint(var_extent_temp):
                    messages.addWarningMessage("Data extents don't overlap.")
        else:
            if (not temp_raster.extent.overlaps(var_extent)) and (
                    not temp_raster.extent.equals(var_extent)):
                messages.addWarningMessage("Data extents don't overlap.")

        # Extract zone data from raster
        arr_zone = arcpy.RasterToNumPyArray(temp_raster, arcpy.Point(xl,yl), \
            ncol, nrow)
        # Flip zone raster to accord with how data is stored
        if blflipx:
            arr_zone = numpy.flipud(arr_zone)
        if blflipy:
            arr_zone = numpy.fliplr(arr_zone)
        if bltranspose:
            arr_zone = numpy.transpose(arr_zone)
        # Delete temporary raster if it exists
        if bltempRaster:
            arcpy.Delete_management(temp_raster)

        # Check if variable is packed
        ispacked = hasattr(arr_var,'scale_factor') or hasattr(arr_var, 'add_offset')
        # Determine whether given statistic is categorical or not
        new_var_dtype = False
        for stat in self.statistics:
            if type_parameter.valueAsText in stat[1].keys():
                new_var_dtype = stat[2]
                break
        type_changed = False
        if ('int' in str(arr_var.dtype)) and (not new_var_dtype) and (
                not ispacked):
            type_changed = True

        # Slice generator
        # Adapted from: http://code.activestate.com/recipes/
        #   502194-a-generator-for-an-arbitrary-number-of-for-loops/
        # Originally written by Steven Bethard
        def multi_for(iterables):
            if not iterables:
                yield ()
            else:
                if isinstance(iterables[0], collections.Iterable):
                    for item in iterables[0]:
                        for rest_tuple in multi_for(iterables[1:]):
                            yield (item,) + rest_tuple
                else:
                    for rest_tuple in multi_for(iterables[1:]):
                        yield (iterables[0],) + rest_tuple

        # Generate slice list
        dim_shape = arr_var.shape
        dim_name = arr_var.dimensions
        dim_slices = []
        dim_dims = []
        dim_prod = 1
        for dim_index, dim_item in enumerate(dim_name):
            if not dim_item in spat_list:
                dim_prod *= dim_shape[dim_index]
                dim_slices.append(xrange(dim_shape[dim_index]))
                dim_dims.append((str(dim_item), numpy.int))
            else:
                dim_slices.append(Ellipsis)

        blstructcreated = False

        def hstack_struct(arr1, arr2):
            # Will only work correctly if arr1 and arr2 only have one record
            dt = numpy.lib.recfunctions.zip_descr((arr1, arr2), flatten=True)
            return numpy.array(arr1.tolist() + arr2.tolist(), dtype = dt)

        # Get zone values
        if noDataValue is not None:
            zones = numpy.setdiff1d(numpy.unique(arr_zone), [noDataValue])
        else:
            zones = numpy.unique(arr_zone)

        # Progress bar
        dim_prod *= zones.size
        arcpy.ResetProgressor()
        arcpy.SetProgressor('step', 'Calculating...', 0, dim_prod, 1)

        # Loop through slices
        index = 0
        valid_indices = []
        for varslice in multi_for(dim_slices):

            # Take slice from data
            if type_changed:
                arr_slice = arr_var[varslice].astype('f8')
            else:
                arr_slice = arr_var[varslice]

            # Create masked array
            if hasattr(arr_slice, 'mask'):
                arr_mask = arr_slice.mask.copy()
            else:
                arr_mask = numpy.ma.make_mask_none(arr_slice.shape)
                arr_slice = numpy.ma.asarray(arr_slice)

            # Loop over zones
            for z in zones:
                # Perform for zone when NoData is ignored
                #   or when there is no NoData within zone
                if ignore_parameter.value or \
                        (not numpy.any((arr_zone==z) & arr_mask)):
                    # Set mask to netCDF NoData mask
                    arr_slice.mask = arr_mask
                    # Apply zone mask
                    arr_slice[arr_zone!=z] = numpy.ma.masked
                    # Apply operator to zone masked slice
                    result = self.calculate_statistic(arr_slice[:], \
                        type_parameter.valueAsText)

                    # Structure results into row
                    struct_data = [dataset.variable(dim_name[it_ind])[it] for \
                        it_ind, it in enumerate(list(varslice)) if \
                        it != Ellipsis]
                    struct_data.append(z)
                    struct_data.append(numpy.ma.count(arr_slice))
                    if numpy.isscalar(result):
                        # Single-valued result
                        struct_data.append(result)
                    else:
                        # Multivalued result
                        struct_data += [it2 for it in result.tolist() for \
                            it2 in it]

                    # Create table when necessary
                    if not blstructcreated:
                        struct_dtype = dim_dims[:]
                        struct_dtype.append((str(zonefield_parameter.value), \
                            numpy.int))
                        struct_dtype.append(('COUNT', numpy.int))
                        if type_parameter.valueAsText in \
                                self.statistics_multiple_values:
                            struct_dtype += [(it, numpy.float) for it in list(
                                result.dtype.names)]
                        else:
                            struct_dtype.append((str(
                                type_parameter.valueAsText), numpy.float))
                        struct = numpy.zeros((dim_prod,), numpy.dtype(struct_dtype))
                        blstructcreated = True

                    # Insert row
                    struct[index] = numpy.array(tuple(struct_data), \
                        numpy.dtype(struct_dtype))

                    valid_indices.append(index)
                #else:
                #    # Passing drops zones with NoData in them from table
                #    pass
                index += 1
                arcpy.SetProgressorPosition()

        arcpy.ResetProgressor()

        if 'time' in dim_name:
            # Output zonal statistics to temporary table
            temp_table = os.path.join(tempfile.gettempdir(), 'temp_table.dbf')
            if arcpy.Exists(temp_table):
                arcpy.Delete_management(temp_table)
            arcpy.da.NumPyArrayToTable(struct[valid_indices], temp_table)
            # Create table view of the time dimension from netCDF file
            temp_mdtable = r"md_table"
            arcpy.MakeNetCDFTableView_md(dataset_name, 'time', temp_mdtable, 'time')
            # Get time field from table view
            desc_fields = arcpy.ListFields(temp_mdtable)
            time_field = desc_fields[[field.name for field in \
                desc_fields].index('time')]
            # Create a table in the output location
            arcpy.CreateTable_management(*os.path.split(output_filename))
            # Add fields from temporary table except for time field, which
            #   we add from the MakeNetCDFTableView
            desc_fields = arcpy.ListFields(temp_table)
            for index, field in enumerate(desc_fields):
                if field.type != 'OID':
                    if field.name == 'time':
                        arcpy.AddField_management(output_filename, time_field.name, \
                            time_field.type, time_field.precision, time_field.scale, \
                            time_field.length, time_field.aliasName, \
                            time_field.isNullable, time_field.required, \
                            time_field.domain)
                    else:
                        arcpy.AddField_management(output_filename, field.name, \
                            field.type, field.precision, field.scale, field.length, \
                            field.aliasName, field.isNullable, field.required,
                            field.domain)
            arcpy.DeleteField_management(output_filename,"Field1")
            # Create list of datetime objects from table view
            time_arc = []
            with arcpy.da.SearchCursor(temp_mdtable, 'time') as cursor:
                for row in cursor:
                    time_arc.append(row[0])
            del cursor
            # Get time variable from netCDF dataset
            time_var = dataset.variable('time')[:].tolist()
            # Loop through entries from temporary table
            with arcpy.da.InsertCursor(output_filename, '*') as ins_cursor:
                new_time_ind = ins_cursor.fields.index('time')
                with arcpy.da.SearchCursor(temp_table, '*') as cursor:
                    time_ind = cursor.fields.index('time')
                    for row in cursor:
                        new_row = list(row)
                        new_row[new_time_ind] = \
                            time_arc[time_var.index(row[time_ind])]
                        ins_cursor.insertRow(tuple(new_row))
            del ins_cursor
            del cursor
        else:
            # Write table
            if arcpy.env.overwriteOutput:
                arcpy.Delete_management(output_filename)
            arcpy.da.NumPyArrayToTable(struct[valid_indices], output_filename)

        return

    def zonal_statistics_as_table_for_discrete(self, parameters, messages, dataset):
        """Performs zonal statistics as table assuming dataset is a CF 1.6
        compliant discrete sampling geometry dataset of 'point', 'timeseries',
        or 'profile' feature type using an orthogonal or incomplete
        multidimensional array data representation."""

        zone_parameter = parameters[0]
        input_parameter = parameters[1]
        variable_parameter = parameters[2]
        output_parameter = parameters[3]
        type_parameter = parameters[4]
        ignore_parameter = parameters[5]
        zonefield_parameter = parameters[6]

        # Grab the parameter values
        dataset_name = input_parameter.valueAsText      # input netCDF filename
        output_filename = output_parameter.valueAsText  # output filename
        var_name = variable_parameter.valueAsText       # netCDF variable name

        # Get associated station, x, and y variables
        (stat_variable, x_variable, y_variable) = self.get_dependent_variables(
            dataset, var_name)
        if (stat_variable is None) or (x_variable is None) or (y_variable is None):
            messages.addErrorMessage('%s is not a station variable.' % var_name)
            raise arcpy.ExecuteError

        # Extract variable from netCDF dataset
        arr_var = dataset.variable(var_name)

        # Extract coordinates attribute
        dim_names = []
        if 'coordinates' in arr_var.ncattrs():
            dim_names = str(arr_var.getncattr('coordinates')).split()

        # Get coordinate arrays
        X = dataset.variable(x_variable)
        Y = dataset.variable(y_variable)

        # Make array of station indices
        if stat_variable in dataset.variable_names():
            arr_stat = dataset.variable(stat_variable)[:]
        else:
            arr_stat = numpy.arange(len(dataset.dimension(stat_variable)))

        # Empty dictionary to hold stations falling within each zone
        zone_stations = {}
        #   where the keys are values of the zone field and the key values
        #   are each a list of station indices contained within that zone

        # Process input zone data
        desc = arcpy.Describe(zone_parameter.value)

        # Was a temporary feature class created?
        bltemppoly = False

        # Convert raster to polygon if necessary
        valid_raster_types = ["RasterLayer", "RasterDataset"]
        valid_feature_types = ["ShapeFile","FeatureLayer", "FeatureDataset"]
        if desc.dataType in valid_raster_types:
            temp_poly = "in_memory\\temp"
            arcpy.RasterToPolygon_conversion(in_raster, temp_poly, \
                "NO_SIMPLIFY", zonefield_parameter.value)
            temp_field = "GRIDCODE"
            bltemppoly = True
        elif desc.dataType in valid_feature_types:
            temp_poly = zone_parameter.value
            temp_field = zonefield_parameter.value
        else:
            messages.addErrorMessage("Not a valid zone dataset.")
            raise arcpy.ExecuteError

        num_recs = int(arcpy.GetCount_management(temp_poly).getOutput(0))
        num_recs *= numpy.prod(arr_stat.shape)

        arcpy.SetProgressor("step", "Building zone feature look-up...", 0, num_recs, 1)

        # Find zones associated with each feature
        desc = arcpy.Describe(temp_poly)
        rows = arcpy.SearchCursor(temp_poly)
        for row in rows:
            feat = row.getValue(desc.ShapeFieldName)
            zone = row.getValue(temp_field)
            for station in arr_stat:
                if feat.contains(arcpy.Point(float(X[station]),float(Y[station]))):
                    if not zone in zone_stations.keys():
                        zone_stations[zone] = []
                    zone_stations[zone].append(station)
                arcpy.SetProgressorPosition()
        del rows, row
        arcpy.ResetProgressor()

        # Delete temporary feature class if it exists
        if bltemppoly:
            arcpy.Delete_management(temp_poly)

        # Check if variable is packed
        ispacked = hasattr(arr_var,'scale_factor') or hasattr(arr_var, 'add_offset')
        # Determine whether given statistic is categorical or not
        new_var_dtype = False
        for stat in self.statistics:
            if type_parameter.valueAsText in stat[1].keys():
                new_var_dtype = stat[2]
                break
        type_changed = False
        if ('int' in str(arr_var.dtype)) and (not new_var_dtype) and (
                not ispacked):
            type_changed = True

        # Slice generator
        # Adapted from: http://code.activestate.com/recipes/
        #   502194-a-generator-for-an-arbitrary-number-of-for-loops/
        # Originally written by Steven Bethard
        def multi_for(iterables):
            if not iterables:
                yield ()
            else:
                if isinstance(iterables[0], collections.Iterable):
                    for item in iterables[0]:
                        for rest_tuple in multi_for(iterables[1:]):
                            yield (item,) + rest_tuple
                else:
                    for rest_tuple in multi_for(iterables[1:]):
                        yield (iterables[0],) + rest_tuple

        # Generate slice list
        dim_shape = arr_var.shape
        dim_name = arr_var.dimensions
        dim_slices = []
        dim_dims = []
        dim_prod = 1
        for dim_index, dim_item in enumerate(dim_name):
            if dim_item != stat_variable:
                dim_prod *= dim_shape[dim_index]
                dim_slices.append(xrange(dim_shape[dim_index]))
                dim_dims.append((str(dim_item), numpy.int))

        # Get position of statistic
        stat_position = dim_name.index(stat_variable)

        blstructcreated = False

        def hstack_struct(arr1, arr2):
            # Will only work correctly if arr1 and arr2 only have one record
            dt = numpy.lib.recfunctions.zip_descr((arr1, arr2), flatten=True)
            return numpy.array(arr1.tolist() + arr2.tolist(), dtype = dt)

        # Progress bar
        dim_prod *= len(zone_stations)
        arcpy.ResetProgressor()
        arcpy.SetProgressor('step', 'Calculating...', 0, dim_prod, 1)

        # Loop through zones
        index = 0
        valid_indices = []
        for zone in zone_stations:

            # Grab station indices associated with zone
            zone_indices = zone_stations[zone]

            # Loop through slices
            for varslice in multi_for(dim_slices):

                # Insert station indices into slice
                varslice = list(varslice)
                varslice.insert(stat_position, zone_indices)

                # Take slice from data
                if type_changed:
                    arr_slice = arr_var[varslice].astype('f8')
                else:
                    arr_slice = arr_var[varslice]

                # Create masked array
                if hasattr(arr_slice, 'mask'):
                    arr_mask = arr_slice.mask.copy()
                else:
                    arr_mask = numpy.ma.make_mask_none(arr_slice.shape)
                    arr_slice = numpy.ma.asarray(arr_slice)

                # Perform for zone when NoData is ignored
                #   or when there is no NoData within zone
                if ignore_parameter.value or (not numpy.any(arr_mask)):

                    # Apply mask
                    arr_slice.mask = arr_mask

                    # Apply operator to zone masked slice
                    result = self.calculate_statistic(arr_slice[:], \
                        type_parameter.valueAsText)

                    # Structure results into row
                    struct_data = []
                    for it_ind, it in enumerate(list(varslice)):
                        if it_ind != stat_position:
                            if dim_name[it_ind] in dataset.variable_names():
                                # Dimension with variable
                                struct_data.append(dataset.variable(dim_name[it_ind])[it])
                            else:
                                # Dimension without variable
                                struct_data.append(it)
                    struct_data.append(zone)
                    struct_data.append(numpy.ma.count(arr_slice))
                    if numpy.isscalar(result):
                        # Single-valued result
                        struct_data.append(result)
                    else:
                        # Multivalued result
                        struct_data += [it2 for it in result.tolist() for it2 in it]

                    # Create table when necessary
                    if not blstructcreated:
                        struct_dtype = dim_dims[:]
                        struct_dtype.append((str(zonefield_parameter.value),numpy.int))
                        struct_dtype.append(('COUNT', numpy.int))
                        if numpy.isscalar(result):
                            # Single-valued result
                            struct_dtype.append((str(type_parameter.valueAsText), \
                                numpy.float))
                        else:
                            # Multivalued result
                            struct_dtype += [(it, numpy.float) for it in list(
                                result.dtype.names)]
                        struct = numpy.zeros((dim_prod,), numpy.dtype(struct_dtype))
                        blstructcreated = True

                    # Insert row
                    struct[index] = numpy.array(tuple(struct_data), \
                        numpy.dtype(struct_dtype))
                    valid_indices.append(index)
                #else:
                #    # Passing drops zones with NoData in them from table
                #    pass
                index += 1
                arcpy.SetProgressorPosition()

        arcpy.ResetProgressor()

        if 'time' in dim_name:
            # Output zonal statistics to temporary table
            temp_table = os.path.join(tempfile.gettempdir(), 'temp_table.dbf')
            if arcpy.Exists(temp_table):
                arcpy.Delete_management(temp_table)
            arcpy.da.NumPyArrayToTable(struct[valid_indices], temp_table)
            # Create table view of the time dimension from netCDF file
            temp_mdtable = r"md_table"
            arcpy.MakeNetCDFTableView_md(dataset_name, 'time', temp_mdtable, 'time')
            # Get time field from table view
            desc_fields = arcpy.ListFields(temp_mdtable)
            time_field = desc_fields[[field.name for field in \
                desc_fields].index('time')]
            # Create a table in the output location
            arcpy.CreateTable_management(*os.path.split(output_filename))
            # Add fields from temporary table except for time field, which
            #   we add from the MakeNetCDFTableView
            desc_fields = arcpy.ListFields(temp_table)
            for index, field in enumerate(desc_fields):
                if field.type != 'OID':
                    if field.name == 'time':
                        arcpy.AddField_management(output_filename, time_field.name, \
                            time_field.type, time_field.precision, time_field.scale, \
                            time_field.length, time_field.aliasName, \
                            time_field.isNullable, time_field.required, \
                            time_field.domain)
                    else:
                        arcpy.AddField_management(output_filename, field.name, \
                            field.type, field.precision, field.scale, field.length, \
                            field.aliasName, field.isNullable, field.required,
                            field.domain)
            arcpy.DeleteField_management(output_filename,"Field1")
            # Create list of datetime objects from table view
            time_arc = []
            with arcpy.da.SearchCursor(temp_mdtable, 'time') as cursor:
                for row in cursor:
                    time_arc.append(row[0])
            del cursor
            # Get time variable from netCDF dataset
            time_var = dataset.variable('time')[:].tolist()
            # Loop through entries from temporary table
            with arcpy.da.InsertCursor(output_filename, '*') as ins_cursor:
                new_time_ind = ins_cursor.fields.index('time')
                with arcpy.da.SearchCursor(temp_table, '*') as cursor:
                    time_ind = cursor.fields.index('time')
                    for row in cursor:
                        new_row = list(row)
                        new_row[new_time_ind] = \
                            time_arc[time_var.index(row[time_ind])]
                        ins_cursor.insertRow(tuple(new_row))
            del ins_cursor
            del cursor
        else:
            # Write table
            if arcpy.env.overwriteOutput:
                arcpy.Delete_management(output_filename)
            arcpy.da.NumPyArrayToTable(struct[valid_indices], output_filename)

        return

    def get_variables_by_dimension(self, dataset, stat_name):
        """List of variables with dimension 'stat_name' and of integer, float,
        or boolean type."""
        var_list = dataset.data_variable_names()
        var_dtypes = ['i','u','f','b']
        var_out = []
        for var_item in var_list:
            var_inst = dataset.variable(var_item)
            if (str(var_inst.dtype.kind) in var_dtypes) and (stat_name in \
                var_inst.dimensions):
                var_out.append(var_item)
        return var_out

    def get_dependent_variables(self, dataset, var_name):
        """Given the name of a netCDF variable, return a tuple of variables
        names cooresponding to (station, x-variable, y-variable) names.  Values
        may be all or partially None for any name undiscovered."""
        # According to CF 1.6 for discrete sampling geometries, "The coordinates
        #   attribute must be attached to every data variable to indicate the
        #   spatiotemporal coordinate variables that are needed to geo-locate
        #   the data."  Additionally, x and y instance variables are mandatory
        #   for all feature types and so will always be indexed by the instance
        #   dimension.
        # Hence, in the following, we read the 'coordinates' attribute of the
        #   variable of interest.  We loop through each listed instance variable
        #   to try to determine the x and y coordinate variables.  Given these
        #   variables, we assume the instance dimension is the rightmost
        #   dimension of the x variable.
        # So, generally, our netCDF file has minimum structure:
        #   DIMENSIONS:
        #       instance = #
        #   VARIABLES:
        #       var_name(..., instance, ...)
        #           .coordinates = "... lon lat ..."
        #       lon(..., instance)
        #       lat(..., instance)

        # Get variable
        arr_var = dataset.variable(var_name)

        # Extract coordinates attribute
        if 'coordinates' in arr_var.ncattrs():
            dim_names = str(arr_var.getncattr('coordinates')).split()
        else:
            return (None, None, None)

        # Coordinate variables can be identified via values of their standard
        # name attribute or values of their units attribute.
        XCoordNamesList = ["longitude","projection_x_coordinate",
                            "grid_longitude"]
        YCoordNamesList = ["latitude","projection_y_coordinate",
                           "grid_longitude"]
        XUnitNamesList = ["degrees_east", "degree_east", "degree_E",
                           "degrees_E", "degreeE", "degreesE" ]
        YUnitNamesList = ["degrees_north","degree_north","degree_N",
                              "degrees_N","degreeN","degreesN"]
        XAxisNameList = ["X"]
        YAxisNameList = ["Y"]

        # Search for x and y variables
        x_variable = ""
        y_variable = ""
        # Loop through each instance variable
        for dim_name in dim_names:
            # Check that a variable actually exists for it (i.e. rather than
            #   being solely a dimension in the dataset).
            if dim_name in dataset.variable_names():
                # Get that variable
                dim_var = dataset.variable(dim_name)
                # Get attribute value if the attribute exists
                if 'standard_name' in dim_var.ncattrs():
                    SNattributeValue = str(dim_var.getncattr('standard_name'))
                else:
                    SNattributeValue = 'missing'
                if 'units' in dim_var.ncattrs():
                    UNattributeValue = str(dim_var.getncattr('units'))
                else:
                    UNattributeValue = 'missing'
                if 'axis' in dim_var.ncattrs():
                    AXattributeValue = str(dim_var.getncattr('axis'))
                else:
                    AXattributeValue = 'missing'
                # Try to discover x and y variables
                if SNattributeValue in XCoordNamesList:
                    x_variable = dim_name
                if SNattributeValue in YCoordNamesList:
                    y_variable = dim_name
                if UNattributeValue in XUnitNamesList:
                    x_variable = dim_name
                if UNattributeValue in YUnitNamesList:
                    y_variable = dim_name
                if AXattributeValue in XAxisNameList:
                    x_variable = dim_name
                if AXattributeValue in YAxisNameList:
                    y_variable = dim_name
        if (not x_variable) or (not y_variable):
            return (None, None, None)

        # Get dimensions of x variable
        stat_variable = dataset.variable_dimension_names(x_variable)

        if len(stat_variable) > 0:
            # Assume instance / station dimension is rightmost dimension
            stat_variable = stat_variable[-1]
        else:
            stat_variable = None

        return (stat_variable, x_variable, y_variable)