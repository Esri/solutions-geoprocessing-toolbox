#-------------------------------------------------------------------------------
# Name  	    	: CIB.pyt
# ArcGIS Version	: ArcGIS 10.3 +
# Script Version	: 20141216
# Name of Company 	: Environmental System Research Institute
# Author        	: ESRI raster solution team
# Purpose 	    	: Collection of tools required for Mosaic Datasets.
# Required Argument 	: Not applicable
# Optional Argument 	: Not applicable
# Usage         	: Load tools_md.pyt within ArcMap
# Copyright	    : (c) ESRI 2014
# License	    : <your license>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import arcpy
from arcpy import env
import sys, os
from datetime import date

solutionLib_path = (os.path.realpath(__file__))
solutionLib_path = os.path.join(os.path.dirname(solutionLib_path), "MDCS/Scripts")
pythonPath = os.path.dirname(os.path.dirname(os.__file__)) + "/python.exe"
configBase = (os.path.dirname(__file__)) + "/MDCS/Parameter/Config/"
sys.path.append(solutionLib_path)

import MDCS


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "CIB Tools"
        self.alias = "cib"

        # List of tool classes associated with this toolbox
        self.tools = [createCIBMD]

class createCIBMD(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create CIB Mosaic"
        self.description = ""
        self.canRunInBackground = True

        self.tool = 'createCIBMD'
#        self.UI = UI()


    def getParameterInfo(self):

        """Define parameter definitions"""
        refGroup = 'Reference Mosaic Datasets'

        workspace = arcpy.Parameter(
        displayName="Target Geodatabase",
        name="workspace",
        datatype="DEType",
        parameterType="Required",
        direction="Input")
        #workspace.filter.list = ["Local Database","File System"]

        md_name = arcpy.Parameter(
        displayName="CIB Mosaic Dataset Name",
        name="md_name",
        datatype="GPString",
        parameterType="Required",
        direction="Input")

        spref = arcpy.Parameter(
        displayName="Coordinate System ",
        name="spref",
        datatype="GPCoordinateSystem",
        parameterType="Required",
        direction="Input")
        spref.value = 4326

        datapath = arcpy.Parameter(
        displayName="Input CIB Data",
        name="datapath",
        #datatype="DEGeodatasetType",
        datatype="DEFolder",
        parameterType="Required",
        direction="Input",
        multiValue=True)

        rastertype = arcpy.Parameter(
        displayName="Raster Type ",
        name="rastertype",
        datatype="GPString",
        parameterType="Required",
        direction="Input")
        rastertype.enabled = True
        rastertype.filter.list = ["Raster Dataset","DTED"]
        rastertype.value = "Raster Dataset"

        parameters = [workspace,md_name,spref,datapath]
        return parameters

    def isLicensed(parameters):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        if (parameters[0].altered == True):
            gdbValue = parameters[0].valueAsText
            mdsValue = ''
            if (parameters[1].altered == True):
                mdsValue = parameters[1].valueAsText

            mdsDesc = arcpy.Describe(parameters[0].value)

            if hasattr(mdsDesc, "dataType"):

                if (mdsDesc.dataType == 'MosaicDataset'):
#                    parameters[2].value = str(mdsDesc.spatialReference.factorycode)
#                    parameters[2].enabled = False

                    if (mdsValue != ''):
                        parameters[0].value = os.path.dirname(gdbValue)
                        if (parameters[1].valueAsText != os.path.basename(gdbValue)):
                            parameters[1].value = os.path.basename(gdbValue)
                    else:
                        parameters[0].value = os.path.dirname(gdbValue)
                        parameters[1].value = os.path.basename(gdbValue)
##                else:
##                    parameters[2].enabled = True

        return parameters

    def updateMessages(self, parameters):
        """ test"""

##        if (parameters[0].altered == True):
##            gdbValue = parameters[0].valueAsText
##            gdbDesc = arcpy.Describe(gdbValue)
##            if hasattr(gdbDesc,"dataType"):
##                if (gdbDesc.dataType != 'Workspace'):
##                    parameters[0].SetErrorMessage("Invalid data type. Select a Mosaic Dataset or Geodatabase.")
##                    return
##                else:
##                    parameters[0].clearMessage
##
##            if (parameters[1].altered == True):
##                mdvalue = parameters[1].valueAsText
##                mdchkValue = arcpy.Exists(os.path.join(gdbValue,mdvalue))
##                if (mdchkValue == False):
##                    if (parameters[2].altered == False):
##                        #parameters[1].SetWarningMessage("New Mosaic Dataset specified, please select the input data.")
##                        pass
##                    else:
##                        parameters[1].clearMessage
##                else:
##                    parameters[1].clearMessage
##
##        return parameters

    def execute(self, parameters, messages):
        """The source code of the tool."""

        for pr in parameters:
            if (pr.hasError() or pr.hasWarning()):
                return

        workspace = parameters[0].valueAsText
        md_name = parameters[1].valueAsText
        datapath = parameters[3].valueAsText
        ssrs = parameters[2].ValueAsText

#        rastertype = parameters[3].valueAsText



        sourceMD = '-m:' + os.path.join(workspace,md_name)
##        if rastertype.lower() == 'raster dataset' :
##            configName = 'Elevation/S_RasterData.xml'
##        elif rastertype.lower() == 'dted' :
##            configName = 'Elevation/S_DTED.xml'
        configName = 'CIB/S_CIB.xml'

        sourcePara = '-i:'+ os.path.join(configBase, configName )
        args = ['rslntm', '#gprun']
        args.append(sourcePara)
        args.append(sourceMD)
        args.append('-b:' + solutionLib_path)
        data = '-s:'+ datapath
        args.append(data)


        ssrsReplace = '-P:' + str(ssrs) + '$' +'sSRS'
        args.append(ssrsReplace)
##        dataID = '-P:' + str(md_name) + '$' + 'did'
##        args.append(dataID)

        messages.addMessage(args)
        argc = len(args)

        ret = MDCS.main(argc, args)


        return
