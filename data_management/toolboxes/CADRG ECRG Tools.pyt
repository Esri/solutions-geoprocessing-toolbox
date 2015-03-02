#-------------------------------------------------------------------------------
# Name  	    	: Tools_MD.pyt
# ArcGIS Version	: ArcGIS 10.1 sp1
# Script Version	: 20130404
# Name of Company 	: Environmental System Research Institute
# Author        	: ESRI raster solution team
# Purpose 	    	: Collection of tools required for Mosaic Datasets.
# Required Argument 	: Not applicable
# Optional Argument 	: Not applicable
# Usage         	: Load tools_md.pyt within ArcMap
# Copyright	    : (c) ESRI 2013
# License	    : <your license>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

import arcpy
from arcpy import env
import sys, os
import tempfile

solutionLib_path = (os.path.realpath(__file__))
solutionLib_path = os.path.join(os.path.dirname(solutionLib_path), "MDCS/Scripts")
pythonPath = os.path.dirname(os.path.dirname(os.__file__)) + "/python.exe"
configBase = (os.path.dirname(__file__)) + "/MDCS/Parameter/Config/"
sys.path.append(solutionLib_path)
tempPath = tempfile.gettempdir()

import MDCS


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "CADRG ECRG Toolbox"
        self.alias = "cadrg"

        # List of tool classes associated with this toolbox
        self.tools = [cadrgecrg]

class cadrgecrg(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "CADRG/ECRG Mosaic Datasets"
        self.description = ""
        self.canRunInBackground = False

        self.tool = 'cadrgecrg'


    def getParameterInfo(self):

        """Define parameter definitions"""
        workspace = arcpy.Parameter(
        displayName="Output Geodatabase",
        name="workspace",
        datatype="DEType",
        parameterType="Required",
        direction="Input")
        #workspace.filter.list = ["Local Database","File System"]

        md_name = arcpy.Parameter(
        displayName="Mosaic Dataset Name",
        name="md_name",
        datatype="GPString",
        parameterType="Required",
        direction="Input")

        datapath = arcpy.Parameter(
        displayName="Input Data Path",
        name="datapath",
        datatype="DEFolder",
        parameterType="Optional",
        direction="Input",
        multiValue=True)

        datafilter = arcpy.Parameter(
        displayName="Data Filter",
        name="datafilter",
        datatype="GPString",
        parameterType="Optional",
        direction="Input")
        datafilter.value = "*.*"

        useoview = arcpy.Parameter(
        displayName="Generate Overviews",
        name="useoview",
        datatype="GPBoolean",
        parameterType="Optional",
        direction="Input")
        useoview.value = False
        useoview.enabled = False

        ovscale = arcpy.Parameter(
        displayName="Overview Scale 1:",
        name="ovscale",
        datatype="GPLong",
        parameterType="Optional",
        direction="Input")
        ovscale.value = 0
        ovscale.enabled = False

        psValue = arcpy.Parameter(
        displayName="Overview scale as Pixel Size:",
        name="psValue",
        datatype="GPDouble",
        parameterType="Optional",
        direction="Input")
        psValue.enabled = False

        spref = arcpy.Parameter(
        displayName="Coordinate System ",
        name="spref",
        datatype="GPCoordinateSystem",
        parameterType="Required",
        direction="Input")
        spref.value = 4326

#        in_worksapce = arcpy.Parameter(
#        displayName="",
#        name="",
#        datatype="",
#        parameterType="",
#        direction="")
        parameters = [workspace,md_name,spref,datapath,datafilter,useoview,ovscale,psValue]
        return parameters

    def isLicensed(parameters):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):



        if parameters[6].valueAstext != '0':
            ps = float((long(parameters[6].valueAstext) * 0.0254) / 96)
            parameters[7].value = ps

        if (parameters[0].altered == True):
            gdbValue = parameters[0].valueAsText
            mdsValue = ''
            if (parameters[1].altered == True):
                mdsValue = parameters[1].valueAsText

            mdsDesc = arcpy.Describe(parameters[0].value)

            if hasattr(mdsDesc, "dataType"):

                if (mdsDesc.dataType == 'MosaicDataset'):

                    if (mdsValue != ''):
                        parameters[0].value = os.path.dirname(gdbValue)
                        if (parameters[1].valueAsText != os.path.basename(gdbValue)):
                            parameters[1].value = os.path.basename(gdbValue)
                    else:
                        parameters[0].value = os.path.dirname(gdbValue)
                        parameters[1].value = os.path.basename(gdbValue)
                        if (arcpy.Exists((os.path.join(os.path.dirname(gdbValue),os.path.basename(gdbValue)))) == True):
                            parameters[5].enabled = True
                            parameters[6].enabled = True
                        else:
                            parameters[5].enabled = False
                            parameters[6].enabled = False
                elif (mdsDesc.dataType == 'Workspace'):
                    if ((parameters[0].altered == True) and (parameters[1].altered == True)):
                        parameters[5].enabled = True
                        parameters[5].enabled = True
                    #pass
                    #return parameters

        if (parameters[1].altered == True):
            mdvalue = parameters[1].valueAsText
            gdbValue = ''
            if (parameters[0].altered == True):
                gdbValue = parameters[0].valueAstext

            mdchkValue = arcpy.Exists(os.path.join(gdbValue,mdvalue))
            if (mdchkValue == False):
                if (parameters[3].altered == False):
                    #parameters[1].SetWarningMessage("New Mosaic Dataset detected. Must pick an input table ")
                    parameters[5].enabled = False
                    parameters[6].enabled = False
                else:
                    #parameters[1].clearMessage
                    parameters[5].enabled = True
                    parameters[6].enabled = True
            else:
                #parameters[1].clearMessage
                parameters[5].enabled = True
                parameters[6].enabled = True

        if ((parameters[5].enabled == True) and (parameters[5].value == True)):
            parameters[6].enabled = True
        else:
            parameters[6].enabled = False

        return parameters

    def updateMessages(self, parameters):
        """ test"""

        if (parameters[0].altered == True):
            gdbValue = parameters[0].valueAsText
            gdbDesc = arcpy.Describe(gdbValue)
            if hasattr(gdbDesc,"dataType"):
                if (gdbDesc.dataType != 'Workspace'):
                    parameters[0].SetErrorMessage("Invalid data type. Select a Mosaic Dataset or Geodatabase.")
                    return
                else:
                    parameters[0].clearMessage

            if (parameters[1].altered == True):
                mdvalue = parameters[1].valueAsText
                mdchkValue = arcpy.Exists(os.path.join(gdbValue,mdvalue))
                if (mdchkValue == False):
                    if (parameters[3].altered == False):
                        parameters[1].SetWarningMessage("New Mosaic Dataset detected, must select a valid input data path.")
                    else:
                        parameters[1].clearMessage
                else:
                    parameters[1].clearMessage

        return parameters
    def execute(self, parameters, messages):
        """The source code of the tool."""

        for pr in parameters:
            if (pr.hasError() or pr.hasWarning()):
                return

        gdbPath = parameters[0].valueAsText
        mdName = parameters[1].valueAsText
        ssrs = parameters[2].ValueAsText
        datapath = parameters[3].valueAsText
        datafilter = parameters[4].valueAsText
        useoview = parameters[5].valueAsText
        ovscale = parameters[6].value

#        args = [pythonPath, os.path.join(solutionLib,'MDCS.py'), '#gprun']
        args = ['rslntm', '#gprun']
        config = '-i:'+ os.path.join(configBase + '/', 'cadrgecrg.xml' )
        args.append(config)
        args.append('-b:' + solutionLib_path)
        full_path = '-m:' + os.path.join(gdbPath, mdName)
        args.append(full_path)

        ssrsReplace = '-P:' + str(ssrs) + '$' +'sSRS'
        args.append(ssrsReplace)
        if (parameters[3].altered == True):
            data = '-s:'+ datapath
            args.append(data)


        if (parameters[3].altered == True):
            if (datafilter == ''):
                datafilter = '#'
                df = '-P:'+datafilter+'$'+'datafilter'
                args.append(df)
            else:
                df = '-P:'+datafilter+'$'+'datafilter'
                args.append(df)
        else:
            datafilter = '#'
            df = '-P:'+datafilter+'$'+'datafilter'
            args.append(df)


        if (parameters[5].value == True):
            if (ovscale > 0):
                #ps = 100
                ps = float((long(ovscale) * 0.0254) / 96)
                varreplace = '-P:'+str(ps)+'$'+'oviewps'
                args.append(varreplace)
            else:
                ps = '#'
        else:
            ps = '#'


        usecmd = ''
        if (parameters[5].value == True):
            if (parameters[3].altered == True):
                usecmd = '-c:' + 'CM+AR+BF+SP+CC+DO+BO'
            else:
                isValidMD = hasattr(arcpy.Describe(os.path.join(gdbPath, mdName)), "dataType")
                if isValidMD:
                    parameters[3].clearMessage
                    usecmd = '-c:' + 'DO+BO'
                else:
                    return

        args.append(usecmd)
        message = usecmd

        messages.addMessage(args)
        argc = len(args)
        ret = MDCS.main(argc, args)

##        p = subprocess.Popen(args, creationflags=subprocess.SW_HIDE, shell=True, stdout=subprocess.PIPE)
##        message = ''
##        while True:
##            message = p.stdout.readline()
##            if not message:
##                break
##            arcpy.AddMessage(message.rstrip())      #remove newline before adding.
        return

