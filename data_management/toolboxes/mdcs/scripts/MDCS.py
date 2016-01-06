#------------------------------------------------------------------------------
# Copyright 2013 Esri
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
# Name: MDCS.py
# Description: This is the main program entry point to MDCS.
# Version: 20150727
# Requirements: ArcGIS 10.1 SP1
# Required Arguments: -i:<config_file>
# Usage: python.exe MDCS.py -c:<Optional:command(s)> -i:<config_file>
# Notes:Type 'python.exe mdcs.py' to display the usage and a list of valid command codes.
# Author: Esri Imagery Workflows team
#------------------------------------------------------------------------------
#!/usr/bin/env python

import arcpy
import sys, os

solutionLib_path = os.path.dirname(__file__)        #set the location to the solutionsLib path
sys.path.append(solutionLib_path)

sys.path.append(os.path.join(solutionLib_path, 'solutionsLog'))
import logger
import solutionsLib     #import Raster Solutions library
import Base

# cli callback ptrs
g_cli_callback = None
g_cli_msg_callback = None
# ends

# cli arcpy callback
def register_for_callbacks(fn_ptr):
    global g_cli_callback
    g_cli_callback = fn_ptr
# ends

# cli msg callback
def register_for_msg_callbacks(fn_ptr):
    global g_cli_msg_callback
    g_cli_msg_callback = fn_ptr
# ends

def postAddData(gdbPath, mdName, info):
    mdName = info['md']
    obvalue = info['pre_AddRasters_record_count']
    fullPath = os.path.join(gdbPath, mdName)

    mosaicMDType = info['type'].lower()
    if(mosaicMDType == 'source'):
        expression = 'OBJECTID >{}'.format(obvalue)
        try:
            fieldName = 'Dataset_ID'
            fieldExist = arcpy.ListFields(fullPath, fieldName)
            if (not fieldExist):
                arcpy.AddField_management(fullPath, fieldName, "TEXT", "", "", "50")
            log.Message('Calculating \'Dataset ID\' for the mosaic dataset ({}) with value ({})'.format(mdName, info[fieldName]), log.const_general_text)
            with arcpy.da.UpdateCursor(fullPath,[fieldName],expression) as rows:
                for row in rows:
                    row[0] = info[fieldName]
                    rows.updateRow(row)
        except:
            log.Message('Err. Failed to calculate \'Dataset_ID\'', log.const_critical_text)
            log.Message(arcpy.GetMessages(), log.const_critical_text)
            return False
    return True

def main(argc, argv):

    if (argc < 2):
    #command-line argument codes.
    #-i:config file.
    #-c:command codes
    #-m:mosaic dataset name
    #-s:Source data paths. (as inputs to command (AR/AR)
    #-l:Full path to log file (including file name)

        user_args = \
        [
        "-m: Mosaic dataset path including GDB and MD name [e.g. c:\WorldElevation.gdb\Portland]",
        "-s: Source data paths. (As inputs to command (AR)",
        "-l: Log file output path [path+file name]",
        "-artdem: Update DEM path in ART file"
        ]

        print ("\nMDCS.py v5.8a [20150611]\nUsage: MDCS.py -c:<Optional:command> -i:<config_file>" \
        "\n\nFlags to override configuration values,") \

        for arg in user_args:
            print (arg)

        print (\
        "\nNote: Commands can be combined with '+' to do multiple operations." \
        "\nAvailable commands:")

        user_cmds = solutionsLib.Solutions().getAvailableCommands()
        for key in user_cmds:
            print ("\t" + key + ' = ' + user_cmds[key]['desc'])
        sys.exit(1)

    base = Base.Base()
    if (not g_cli_callback is None):
        base.m_cli_callback_ptr = g_cli_callback
    if (not g_cli_msg_callback is None):
        base.m_cli_msg_callback_ptr = g_cli_msg_callback
    global log
    log = logger.Logger(base);
    base.setLog(log)

    argIndx = 0
    md_path_ = artdem = config = com = log_folder = code_base =  ''

    while(argIndx < argc):
        (values) = argv[argIndx].split(':')
        if (len(values[0]) < 2 or
            values[0][:1] != '-' and
            values[0][:1] != '#'):
            argIndx += 1
            continue

        exSubCode = values[0][1:len(values[0])].lower()
        subCode = values.pop(0)[1].lower()

        value = ':'.join(values).strip()

        if (subCode == 'c'):
            com = value.replace(' ', '')        #remove spaces in between.
        elif(subCode == 'i'):
            config = value
        elif(subCode == 'm'):
            md_path_ = value
        elif(subCode == 's'):
            base.m_sources = value
        elif(subCode == 'l'):
            log_folder =  value
        elif(subCode == 'b'):
            code_base =  value
        elif(exSubCode == 'artdem'):
            artdem =  value
        elif(exSubCode == 'gprun'):
            log.isGPRun = True                  # direct log messages also to (arcpy.AddMessage)
        elif(subCode == 'p'):
            pMax = value.rfind('$')
            if (pMax == -1):
                argIndx += 1
                continue

            dynamic_var = value[pMax + 1:].upper()
            v =  value[0: pMax]
            if (dynamic_var.strip() != ''):
                if ((dynamic_var in base.m_dynamic_params.keys()) == False):
                    base.m_dynamic_params[dynamic_var] = v

        argIndx += 1


    if (code_base != ''):
        base.setCodeBase(code_base)


    if (md_path_ != ''):
        (p, f) = os.path.split(md_path_)
        f = f.strip()
        const_gdb_ext_len_ = len(base.const_geodatabase_ext)
        ext = p[-const_gdb_ext_len_:].lower()
        if ((ext == base.const_geodatabase_ext.lower() or
            ext == base.const_geodatabase_SDE_ext.lower()) and
            f != ''):
            p = p.replace('\\', '/')
            w = p.split('/')
            workspace_ = ''
            for i in range(0, len(w) - 1):
                workspace_ += w[i] + '/'

            gdb_ = w[len(w) -1]
            base.m_workspace = workspace_
            base.m_geodatabase = w[len(w) - 1]
            base.m_mdName = f


    configName, ext = os.path.splitext(config)
    configName = os.path.basename(configName)

    # setup log
    log.Project ('MDCS')
    log.LogNamePrefix(configName)
    log.StartLog()

    log_output_folder  = os.path.join(os.path.dirname(solutionLib_path), 'logs')

    if (log_folder != ''):
        (path, fileName) = os.path.split(log_folder)
        if (path != ''):
            log_output_folder = path
        if (fileName != ''):
            log.LogFileName(fileName)

    log.SetLogFolder(log_output_folder)
    # ends

    if (os.path.isfile(config) == False):
        log.Message('Input config file is not specified/not found! ({})'.format(config), logger.Logger.const_critical_text)
        log.Message(base.CCMD_STATUS_FAILED, logger.Logger.const_status_text)    # set (failed) status
        log.WriteLog('#all')
        return False

    if (artdem != ''):
        (base.m_art_ws, base.m_art_ds) = os.path.split(artdem)
        base.m_art_apply_changes = True

    comInfo = {
    'AR' : { 'cb' : postAddData }       #assign a callback function to run custom user code when adding rasters.
    }

    if (com == ''):
        com = base.const_cmd_default_text

    solutions = solutionsLib.Solutions(base)
    success = solutions.run(config, com, comInfo)

    log.Message ("Done...", log.const_general_text)
    log.WriteLog('#all')   #persist information/errors collected.

if __name__ == '__main__':
    main(len(sys.argv), sys.argv)


