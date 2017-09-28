# -*- coding: utf-8 -*-
import os.path
import tempfile
import arcpy
import tool


class NetCDFTool(tool.Tool):

    @staticmethod
    def default_output_directory_name(
            input_path_name):
        """
        Return the default output directory name.
        """
        workspace = arcpy.env.workspace

        if workspace is None:
            workspace = os.path.dirname(input_path_name)

            if not os.path.isdir(workspace):
                workspace = tempfile.gettempdir()
        else:
            while arcpy.Describe(workspace).datatype != "Folder":
                workspace = os.path.dirname(workspace)

        return workspace

    @staticmethod
    def parameter_must_be_initialized(
            parameter,
            dataset_parameter):
        """
        Return whether *parameter* must be initialized or not.

        parameter
           Parameter to check.

        dataset_parameter
           Dataset parameter.

        The *parameter* passed in must be initialized if either:

        * The user asks for it (*parameter* is not altered and value is None).
        * The *dataset_parameter* is new and *parameter* is not altered yet
          (*parameter* is not altered and *dataset_parameter*  is new).

        When initializing *parameter*:

        * Reset to empty if *dataset_parameter* is None.
        * Reset to values if *dataset_parameter* is not None.
        """
        assert parameter is not None
        assert dataset_parameter is not None
        return \
            (tool.Tool.parameter_is_new(dataset_parameter) and \
                (not parameter.altered)) or \
            tool.Tool.parameter_must_be_initialized(parameter)

    @staticmethod
    def parameter_must_be_updated(
            parameter,
            dataset_parameter):
        """
        Return whether *parameter* must be updated or not.

        parameter
           Parameter to check.

        dataset_parameter
           Dataset parameter.

        The *parameter* passed in must be updated if:

        * The *dataset_parameter* is new and *parameter* is altered.
        """
        assert parameter is not None
        assert dataset_parameter is not None
        return parameter.altered and \
            tool.Tool.parameter_is_new(dataset_parameter)

    def __init__(self):
        tool.Tool.__init__(self)
