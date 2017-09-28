# -*- coding: utf-8 -*-
import os.path
import sys
import arcpy

sys.path.append(os.path.join(os.path.dirname(__file__), "Scripts"))
import mds

import mds.tools.opendap_to_netcdf as opendap_to_netcdf
import mds.tools.describe_multidimensional_dataset as \
    describe_multidimensional_dataset
import mds.tools.make_netcdf_regularpointslayer as \
    make_netcdf_regularpoints_layer
import mds.tools.make_netcdf_stationpointslayer as \
    make_netcdf_stationpoints_layer
import mds.tools.make_netcdf_trajectorypointslayer as \
    make_netcdf_trajectorypoints_layer
import mds.tools.get_variable_statistics as \
    get_variable_statistics
import mds.tools.get_variable_statistics_over_dimension as \
    get_variable_statistics_over_dimension
import mds.tools.multidimensional_zonal_statistics as \
    multidimensional_zonal_statistics
import mds.tools.multidimensional_zonal_statistics_as_table as \
    multidimensional_zonal_statistics_as_table

opendap_to_netcdf = reload(opendap_to_netcdf)
describe_multidimensional_dataset = reload(describe_multidimensional_dataset)
make_netcdf_regularpoints_layer = reload(make_netcdf_regularpoints_layer)
make_netcdf_stationpoints_layer = reload(make_netcdf_stationpoints_layer)
make_netcdf_trajectorypoints_layer = reload(make_netcdf_trajectorypoints_layer)
get_variable_statistics = reload(get_variable_statistics)
get_variable_statistics_over_dimension = reload(get_variable_statistics_over_dimension)
multidimensional_zonal_statistics = reload(multidimensional_zonal_statistics)
multidimensional_zonal_statistics_as_table = reload(
    multidimensional_zonal_statistics_as_table)

OPeNDAPtoNetCDF = opendap_to_netcdf.OPeNDAPtoNetCDF
DescribeMultidimensionalDataset = \
    describe_multidimensional_dataset.DescribeMultidimensionalDataset
MakeNetCDFRegularPointsLayer = \
    make_netcdf_regularpoints_layer.MakeNetCDFRegularPointsLayer
MakeNetCDFStationPointsLayer = \
    make_netcdf_stationpoints_layer.MakeNetCDFStationPointsLayer
MakeNetCDFTrajectoryPointsLayer = \
    make_netcdf_trajectorypoints_layer.MakeNetCDFTrajectoryPointsLayer
GetVariableStatistics = \
    get_variable_statistics.GetVariableStatistics
GetVariableStatisticsOverDimension = \
    get_variable_statistics_over_dimension.GetVariableStatisticsOverDimension
MultidimensionalZonalStatistics = \
    multidimensional_zonal_statistics.MultidimensionalZonalStatistics
MultidimensionalZonalStatisticsAsTable = \
    multidimensional_zonal_statistics_as_table.MultidimensionalZonalStatisticsAsTable

class Toolbox(object):

    def __init__(self):
        self.label = "Multidimension Supplemental Tools"
        self.alias = "mds"
        self.description = "This toolbox contains supplemental tools for " \
            "the ArcGIS Multidimension toolbox."
        self.tools = [OPeNDAPtoNetCDF,
                      DescribeMultidimensionalDataset,
                      MakeNetCDFRegularPointsLayer,
                      MakeNetCDFStationPointsLayer,
                      MakeNetCDFTrajectoryPointsLayer,
					  GetVariableStatistics,
                      GetVariableStatisticsOverDimension,
                      MultidimensionalZonalStatistics,
                      MultidimensionalZonalStatisticsAsTable]


# vim:syntax=python
