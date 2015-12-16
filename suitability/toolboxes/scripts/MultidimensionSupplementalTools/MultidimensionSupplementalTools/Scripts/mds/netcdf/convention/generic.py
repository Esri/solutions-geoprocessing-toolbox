# -*- coding: utf-8 -*-
import mds.ordered_set
import convention
import units


class Generic(convention.Convention):
    """
    This class can be used in case there is no convention attribute present
    in the netcdf file, or if the convention that is mentioned is unsupported.

    This class implements the `generic attribute conventions`_ convention.

    .. _generic attribute conventions: http://www.unidata.ucar.edu/software/netcdf/docs/attribute_conventions.html

    .. todo::

       Merge this class with :py:class:`convention.Convention` and let the
       other conventions override the default implementations.
    """

    @staticmethod
    def conforms(
            dataset):
        """
        Return whether or not the *dataset* conforms to the convention.

        This function always returns True.
        """
        return True

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

            # Variable must be one-dimensional.
            if len(variable.dimensions) == 1:
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
