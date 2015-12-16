#------------------------------------------------------------------------------
# Copyright 2015 Esri
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------
# Name  	    	: Elevation Tools.pyt
# ArcGIS Version	: ArcGIS 10.3 +
# Script Version	: 20141216
# Name of Company 	: Environmental System Research Institute
# Author        	: ESRI raster solution team
# Purpose 	    	: Collection of tools required for Mosaic Datasets.
# Required Argument 	: Not applicable
# Optional Argument 	: Not applicable
# Usage         	: Load Elevation Tools.pyt within ArcMap
# Copyright	    : (c) ESRI 2015
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
        self.label = "Elevation Tools"
        self.alias = "elev"

        # List of tool classes associated with this toolbox
        self.tools = [createSourceMD,createDerivedMD]

class createSourceMD(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create Source Elevation Mosaic"
        self.description = ""
        self.canRunInBackground = True

        self.tool = 'createSourceMD'
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
        displayName="Source Elevation Mosaic Dataset Name",
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
        displayName="Input Elevation Data",
        name="datapath",
        #datatype="DEGeodatasetType",
        datatype="DEFolder",
        parameterType="Required",
        direction="Input")

        rastertype = arcpy.Parameter(
        displayName="Raster Type ",
        name="rastertype",
        datatype="GPString",
        parameterType="Required",
        direction="Input")
        rastertype.enabled = True
        rastertype.filter.list = ["Raster Dataset","DTED"]
        rastertype.value = "Raster Dataset"

        parameters = [workspace,md_name,spref,rastertype,datapath]
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
                    parameters[2].value = str(mdsDesc.spatialReference.factorycode)
                    parameters[2].enabled = False

                    if (mdsValue != ''):
                        parameters[0].value = os.path.dirname(gdbValue)
                        if (parameters[1].valueAsText != os.path.basename(gdbValue)):
                            parameters[1].value = os.path.basename(gdbValue)
                    else:
                        parameters[0].value = os.path.dirname(gdbValue)
                        parameters[1].value = os.path.basename(gdbValue)
                else:
                    parameters[2].enabled = True

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
        datapath = parameters[4].valueAsText
        ssrs = parameters[2].ValueAsText

        rastertype = parameters[3].valueAsText



        sourceMD = '-m:' + os.path.join(workspace,md_name)
        if rastertype.lower() == 'raster dataset' :
            configName = 'Elevation/S_RasterData.xml'
        elif rastertype.lower() == 'dted' :
            configName = 'Elevation/S_DTED.xml'
        sourcePara = '-i:'+ os.path.join(configBase, configName )
        args = ['rslntm', '#gprun']
        args.append(sourcePara)
        args.append(sourceMD)
        args.append('-b:' + solutionLib_path+ "/base")
        data = '-s:'+ datapath
        args.append(data)


        ssrsReplace = '-P:' + str(ssrs) + '$' +'sSRS'
        args.append(ssrsReplace)
        dataID = '-P:' + str(md_name) + '$' + 'did'
        args.append(dataID)

        messages.addMessage(args)
        argc = len(args)

        ret = MDCS.main(argc, args)


        return

class createDerivedMD(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create Derived Elevation Mosaic"
        self.description = ""
        self.canRunInBackground = True

        self.tool = 'createSourceMD'
#        self.UI = UI()


    def getParameterInfo(self):

        """Define parameter definitions"""

        workspace = arcpy.Parameter(
        displayName="Target Geodatabase",
        name="workspace",
        datatype="DEType",
        parameterType="Required",
        direction="Input")
        #workspace.filter.list = ["Local Database","File System"]

        md_name = arcpy.Parameter(
        displayName="Derived Elevation Mosaic Dataset Name",
        name="md_name",
        datatype="GPString",
        parameterType="Required",
        direction="Input")

        datapath = arcpy.Parameter(
        displayName="Input Elevation Data",
        name="datapath",
        #datatype="DEGeodatasetType",
        datatype="GPMosaicLayer",
        parameterType="Required",
        direction="Input")
        datapath.multiValue = True

        dspref = arcpy.Parameter(
        displayName="Coordinate System",
        name="dspref",
        datatype="GPCoordinateSystem",
        parameterType="Required",
        direction="Input")
        dspref.value = 4326

        parameters = [workspace,md_name,dspref,datapath]
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

                    parameters[2].value = str(mdsDesc.spatialReference.factorycode)
                    parameters[2].enabled = False

                    if (mdsValue != ''):
                        parameters[0].value = os.path.dirname(gdbValue)
                        if (parameters[1].valueAsText != os.path.basename(gdbValue)):
                            parameters[1].value = os.path.basename(gdbValue)
                    else:
                        parameters[0].value = os.path.dirname(gdbValue)
                        parameters[1].value = os.path.basename(gdbValue)
                else:
                    parameters[2].enabled = True

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
##                    if (parameters[3].altered == False):
##                        #parameters[1].SetWarningMessage("New Mosaic Dataset specified, please select the input data.")
##                        pass
##                    else:
##                        parameters[1].clearMessage
##                else:
##                    parameters[1].clearMessage

        return parameters

    def execute(self, parameters, messages):
        """The source code of the tool."""

        for pr in parameters:
            if (pr.hasError() or pr.hasWarning()):
                return

        dworkspace = parameters[0].valueAsText
        dmd_name = parameters[1].valueAsText
        dsrs = parameters[2].valueAsText
        ddatapath = parameters[3].valueAsText

        derivedMD = '-m:' + os.path.join(dworkspace,dmd_name)

        configName = 'Elevation/D_Mosaic.xml'
        derivedPara = '-i:'+ os.path.join(configBase, configName )

#        dargs = [pythonPath, os.path.join(solutionLib_path,'MDCS.py'), '#gprun']
        dargs = ['rslntm', '#gprun']
        dargs.append(derivedPara)
        dargs.append(derivedMD)
        dargs.append('-b:' + solutionLib_path + "/base")
        dsrsReplace = '-P:' + str(dsrs) + '$' +'sSRS'
        dargs.append(dsrsReplace)

        ddata = '-s:'+ ddatapath
        dargs.append(ddata)
        messages.addMessage(dargs)
        argc = len(dargs)
        ret = MDCS.main(argc, dargs)

        return