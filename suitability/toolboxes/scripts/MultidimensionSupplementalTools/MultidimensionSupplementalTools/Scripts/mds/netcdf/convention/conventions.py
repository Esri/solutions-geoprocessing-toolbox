# -*- coding: utf-8 -*-
import mds.ordered_set
import convention


class Conventions(convention.Convention):
    """
    This is a class that layers the conventions supported by this package
    and used by the dataset. This class will use all conventions and
    checks whether they all behave the same. This is mainly useful for
    debugging.
    """

    def __init__(self,
            dataset,
            filter_out_nd_coordinates,
            conventions):
        convention.Convention.__init__(self, dataset, filter_out_nd_coordinates)
        self.conventions = conventions

    def assert_equal_result_from_each_convention(self,
            result):
        for i in range(1, len(result)):
            assert result[i] == result[0], "{} ({}) != {} ({})".format(
                result[i], type(self.conventions[i]),
                result[0], type(self.conventions[0]))

    def coordinate_variable_names(self,
            variable_name):
        result = []
        for convention in self.conventions:
            result.append(convention.coordinate_variable_names(variable_name))
        self.assert_equal_result_from_each_convention(result)
        return result[0]

    def is_space_dimension_variable(self,
            variable):
        result = []
        for convention in self.conventions:
            result.append(convention.is_space_dimension_variable(variable))
        self.assert_equal_result_from_each_convention(result)
        return result[0]

    def space_dimension_names(self,
            variable_name):
        result = []
        for convention in self.conventions:
            result.append(convention.space_dimension_names(variable_name))
        self.assert_equal_result_from_each_convention(result)
        return result[0]

    def time_dimension_names(self,
            variable_name):
        result = []
        for convention in self.conventions:
            result.append(convention.time_dimension_names(variable_name))
        self.assert_equal_result_from_each_convention(result)
        return result[0]

    def data_variable_names(self):
        result = []
        for convention in self.conventions:
            result.append(convention.data_variable_names())
        self.assert_equal_result_from_each_convention(result)
        return result[0]

    def spatial_data_variable_names(self):
        result = []
        for convention in self.conventions:
            result.append(convention.spatial_data_variable_names())
        self.assert_equal_result_from_each_convention(result)
        return result[0]

    def temporal_variable_names(self):
        result = []
        for convention in self.conventions:
            result.append(convention.temporal_variable_names())
        self.assert_equal_result_from_each_convention(result)
        return result[0]

    def is_spatial_variable(self,
            variable_name):
        result = []
        for convention in self.conventions:
            result.append(convention.is_spatial_variable(variable_name))
        self.assert_equal_result_from_each_convention(result)
        return result[0]

    def extent(self,
            variable_name):
        result = []
        for convention in self.conventions:
            result.append(convention.extent(variable_name))
        self.assert_equal_result_from_each_convention(result)
        return result[0]

    def spatial_dimension_slices(self,
            variable_name,
            extent):
        result = []
        for convention in self.conventions:
            result.append(convention.spatial_dimension_slices(variable_name,
                extent))
        self.assert_equal_result_from_each_convention(result)
        return result[0]

    def compatible_data_variable_names(self,
            variable_name):
        result = []
        for convention in self.conventions:
            result.append(convention.compatible_data_variable_names(
                variable_name))
        self.assert_equal_result_from_each_convention(result)
        return result[0]

    def dependent_variable_names(self,
            variable_name):
        result = []
        for convention in self.conventions:
            result.append(convention.dependent_variable_names(variable_name))
        self.assert_equal_result_from_each_convention(result)
        return result[0]

    def is_time_dimension_variable(self,
            variable):
        result = []
        for convention in self.conventions:
            result.append(convention.is_time_dimension_variable(variable))
        self.assert_equal_result_from_each_convention(result)
        return result[0]
