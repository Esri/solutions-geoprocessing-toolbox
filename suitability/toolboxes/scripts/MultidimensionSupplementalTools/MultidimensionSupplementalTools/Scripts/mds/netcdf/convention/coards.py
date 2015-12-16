# -*- coding: utf-8 -*-
import mds.ordered_set
import convention
import units


class Coards(convention.Convention):
    """
    This class implements the `Cooperative Ocean/Atmosphere Research Data
    Service Convention`_.

    .. _Cooperative Ocean/Atmosphere Research Data Service Convention: http://ferret.wrc.noaa.gov/noaa_coop/coop_cdf_profile.html

    By definition, coordinate variables are one-dimensional. This means that
    the *filter_out_nd_coordinates* setting is not relevant.
    """

    @staticmethod
    def conforms(
            dataset):
        return "COARDS" in convention.Convention.convention_names(dataset)

    def __init__(self,
            dataset,
            filter_out_nd_coordinates):
        convention.Convention.__init__(self, dataset, filter_out_nd_coordinates)

    def is_coordinate_variable(self,
            variable_name):
        result = False
        assert variable_name in self.dataset.variables, variable_name
        variable = self.dataset.variables[variable_name]

        # Variable and dimension names must be equal.
        if variable_name in self.dataset.dimensions:

            # Variable must be one-dimensional and have a numeric data type.
            if len(variable.dimensions) == 1:
                if units.is_numeric(variable.dtype):
                    result = True

        return result

    def is_x_dimension_variable(self,
            variable):
        return hasattr(variable, "units") and units.is_longitude(variable.units)

    def is_y_dimension_variable(self,
            variable):
        return hasattr(variable, "units") and units.is_latitude(variable.units)

    def is_time_dimension_variable(self,
            variable):
        variable = self.dataset.variables[variable] if isinstance(variable,
            basestring) else variable
        return hasattr(variable, "units") and units.is_time(variable.units)

    def is_data_variable(self,
            variable_name):
        return not self.is_coordinate_variable(variable_name)

    def dependent_variable_names(self,
            variable_name):
        return mds.ordered_set.OrderedSet()
