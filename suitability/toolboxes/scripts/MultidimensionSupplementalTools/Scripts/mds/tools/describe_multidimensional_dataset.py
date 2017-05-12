# -*- coding: utf-8 -*-
import mds
import mds.messages
import arcpy


class DescribeMultidimensionalDataset(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Describe Multidimensional Dataset"
        self.description = "Lists the metadata of a local or remote " + \
        "multidimensional dataset, such as netCDF or HDF. "
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
        displayName="Input File or URL String",
        name="in_dataset",
        datatype=["DEFile","GPString"],
        parameterType="Required",
        direction="Input")

    # Second parameter
        param1 = arcpy.Parameter(
        displayName="Output Report File",
        name="output_report_file",
        datatype="DEFile",
        parameterType="Optional",
        direction="Output")

        params = [param0, param1]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        if parameters[0].value:
            try:
                dataset = mds.netcdf.Dataset(parameters[0].valueAsText, '')

            except RuntimeError, exception:
                if "No such file or directory" in str(exception) or \
                    "Invalid argument" in str(exception):
                    parameters[0].setErrorMessage(
                        mds.messages.INPUT_DATASET_DOES_NOT_RESOLVE_TO_FILENAME.format(
                            parameters[0].valueAsText))
                elif "Malformed or inaccessible DAP DDS" in str(exception):
                    parameters[0].setErrorMessage(
                        mds.messages.INPUT_DATASET_URL_MALFORMED.format(
                            parameters[0].valueAsText))
                else:
                    parameters[0].setErrorMessage(
                        mds.messages.INPUT_DATASET_GENERIC_ERROR.format(
                            parameters[0].valueAsText, str(exception)))
            except Exception, exception:
                parameters[0].setErrorMessage(
                    mds.messages.INPUT_DATASET_GENERIC_ERROR.format(
                        parameters[0].valueAsText, str(exception)))

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        def pprint(text):
            """Override print statement."""
            arcpy.AddMessage(text)
            if (parameters[1].value):
                print >> f, text
            return

        try:
            dataset_name = parameters[0].valueAsText
            dataset = mds.netcdf.Dataset(dataset_name,'')
        except RuntimeError, exception:
            # Handle errors not detected by updateMessages.
            messages.addErrorMessage(str(exception))
            raise arcpy.ExecuteError

        # If user specified an output file, open it for writing
        if parameters[1].value:
            f = open(parameters[1].valueAsText, 'w')
        # Print file, netCDF file type, and dimensions.
        pprint("\n")
        pprint("netcdf file: " + parameters[0].valueAsText + "  (" + \
        dataset.dataset.file_format + ")")
        pprint("dimensions:")

        for dimobj in dataset.dataset.dimensions.values():
            if dimobj.isunlimited(): # dimension is unlimited
                pprint("\t" + dimobj._name + " = UNLIMITED\t// (" + "(" + \
                 str(len(dimobj)) + " currently)")
            else:
                pprint("\t" + dimobj._name + " = " + str(len(dimobj)))

        # Print information on variables
        pprint("variables:")

        for varname in dataset.dataset.variables.values():
            dim_list = []
            for d in varname.dimensions:
                dim_list.append(dataset.dataset.dimensions[d]._name + "=" + \
                str(dataset.dataset.dimensions[d].__len__()))
            dim_list = ', '.join(dim_list)
            pprint("\t" + str(varname.dtype) + " " + varname._name + \
            "(" + dim_list + ")")
            for attribute_name in varname.ncattrs():
                pprint("\t\t:" + attribute_name + " = " + \
                str(getattr(varname, attribute_name)))

        # Print global attributes
        pprint("global atributes:")
        for name in dataset.dataset.ncattrs():
            pprint('\t' + name + '=' + str(getattr(dataset.dataset, name)))

        if parameters[1].value:
            f.flush()
            f.close()

        return