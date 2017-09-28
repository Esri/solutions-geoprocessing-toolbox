# -*- coding: utf-8 -*-
import mds.ordered_set
import coards


def is_x(
        variable):
    result = False
    if hasattr(variable, "standard_name") and "x_coordinate" in \
            variable.standard_name:
        result = True
    return result


def is_y(
        variable):
    result = False
    if hasattr(variable, "standard_name") and "y_coordinate" in \
            variable.standard_name:
        result = True
    return result


class CF(coards.Coards):
    """
    This class implements the `Climate and Forecast Metadata Convention`_.

    .. _Climate and Forecast Metadata Convention: http://cf-pcmdi.llnl.gov
    """

    @staticmethod
    def conforms(
            dataset):
        return any(["CF-" in name for name in CF.convention_names(dataset)])

    def __init__(self,
            dataset,
            filter_out_nd_coordinates):
        coards.Coards.__init__(self, dataset, filter_out_nd_coordinates)

    def is_coordinate_variable(self,
            variable_name):
        result = coards.Coards.is_coordinate_variable(self, variable_name)

        if result is False:
            # Variable must be listed in coordinates attribute of some other
            # variable.
            attribute_values = self.variable_attribute_values("coordinates")
            attribute_values = [value.split() for value in attribute_values]
            result = any([variable_name in values for values in
                attribute_values])

        return result

    def is_x_dimension_variable(self,
            variable):
        return coards.Coards.is_x_dimension_variable(self, variable) or \
            is_x(variable)

    def is_y_dimension_variable(self,
            variable):
        return coards.Coards.is_y_dimension_variable(self, variable) or \
            is_y(variable)

    def is_data_variable(self,
            variable_name):
        return coards.Coards.is_data_variable(self, variable_name) and \
            not self.is_grid_mapping_variable(variable_name) and \
            not (
                self.filter_out_nd_coordinates and
                self.depends_on_nd_coordinate_variable(variable_name)
            )

    def is_grid_mapping_variable(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name

        variable = self.dataset.variables[variable_name]
        return hasattr(variable, "grid_mapping_name")

    def dependent_variable_names(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name
        variable = self.dataset.variables[variable_name]
        result = []

        if hasattr(variable, "ancillary_variables"):
            result += variable.ancillary_variables.split()

        if hasattr(variable, "coordinates"):
            result += variable.coordinates.split()

        if hasattr(variable, "grid_mapping"):
            result.append(variable.grid_mapping.strip())

        return result
