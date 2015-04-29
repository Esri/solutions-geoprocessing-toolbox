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
# Name: Base.py
# Description: Base class used by MDCS/All Raster Solutions components.
# Version: 20140417
# Requirements: ArcGIS 10.1 SP1
# Author: Esri Imagery Workflows team
#------------------------------------------------------------------------------
#!/usr/bin/env python

import os
import sys
import arcpy

if (sys.version_info[0] < 3):           # _winreg has been renamed as (winreg) in python3+
    from _winreg import *
else:
    from winreg import *

from datetime import datetime

from xml.dom import minidom

try:
    import MDCS_UC
except Exception as inf:
    print ('User-Code functions disabled.')


class Base(object):

#begin - constansts
    const_general_text = 0
    const_warning_text = 1
    const_critical_text = 2
    const_status_text = 3

    const_cmd_default_text = "#defaults"
    const_geodatabase_ext = '.GDB'
    const_geodatabase_SDE_ext = '.SDE'

    # base init codes. (const_strings)
    const_init_ret_version = 'version'
    const_init_ret_sde = 'sde'
    const_init_ret_patch = 'patch'
    # ends


    #version specific
    const_ver_len = 4

    CMAJOR = 0
    CMINOR = 1
    CSP = 2
    CBUILD = 3
    CVERSION_ATTRIB = 'version'

    # ends

    # externally user defined functions specific
    CCLASS_NAME = 'UserCode'
    CMODULE_NAME = 'MDCS_UC'
    # ends



#ends

    def __init__(self):
        self.m_log = None
        self.m_doc = None

#the follwoing variables could be overridden by the command-line to replace respective values in XML config file.
        self.m_workspace = ''
        self.m_geodatabase = ''
        self.m_mdName = ''  #mosaic dataset name.
#ends

        self.m_sources = ''

        self.m_gdbName = ''
        self.m_geoPath = ''
        self.m_config = ''
        self.m_commands = ''

        self.m_sources = ''  #source data paths for adding new rasters.

        self.m_dynamic_params = {}

        # art file update specific variables
        self.m_art_apply_changes = ''
        self.m_art_ws = ''
        self.m_art_ds = ''
        # ends

        # To keep track of the last objectID before any new data items could be added.
        self.m_last_AT_ObjectID = 0     #by default, take in all the previous records for any operation.


        # SDE specific variables
        self.m_IsSDE = False
        self.m_SDE_database_user = ''
        # ends

        # set MDCS code base path
        self.m_code_base = ''
        self.setCodeBase(os.path.dirname(__file__))
        # ends



    def init(self):         #return (status [true|false], reason)

        if (self.m_doc == None):
            return False

        #version check.
        try:

            min = self.getXMLXPathValue("Application/ArcGISVersion/Product/Min", "Min").split('.')
            max = self.getXMLXPathValue("Application/ArcGISVersion/Product/Max", "Max").split('.')

            if (len(min) == self.const_ver_len): #version check is disabled if no values have been defined in the MDCS for min and max.

                CMAJOR = 0
                CBUILD = self.const_ver_len

                if (len(max) != self.const_ver_len):
                    max = [0, 0, 0, 0]               # zero up max if max version isn't defined / has errors.

                for n in range(CMAJOR, CBUILD):
                    if (min[n] == ''):
                        min[n] = 0
                    if (max[n] == ''):
                        max[n] = 0

                    min[n] = int(min[n])
                    max[n] = int(max[n])

                if (self.CheckMDCSVersion(min, max) == False):
                    return (False, self.const_init_ret_version)        #version check failed.

        except Exception as inst:
            self.log('Version check failure/' + str(inst), self.const_critical_text)
            return False
        #ends


        # ArcGIS patch test.
        if (self.isArcGISPatched() == False):
            self.log('An ArcGIS patch required to run MDCS is not yet installed. Unable to proceed.', self.const_critical_text)
            return (False, self.const_init_ret_patch)
        # ends


        self.setUserDefinedValues()         #replace user defined dynamic variables in config file with values provided at the command-line.

        if (self.m_workspace == ''):
            self.m_workspace = self.prefixFolderPath(self.getAbsPath(self.getXMLNodeValue(self.m_doc, "WorkspacePath")), self.const_workspace_path_)

        if (self.m_geodatabase == ''):
            self.m_geodatabase =  self.getXMLNodeValue(self.m_doc, "Geodatabase")

        if (self.m_mdName == ''):
            self.m_mdName =  self.getXMLXPathValue("Application/Workspace/MosaicDataset/Name", "Name")


        const_len_ext = len(self.const_geodatabase_ext)
        ext = self.m_geodatabase[-const_len_ext:].upper()
        if (ext != self.const_geodatabase_ext and
            ext != self.const_geodatabase_SDE_ext):
            self.m_geodatabase += self.const_geodatabase_ext.lower()        #if no extension specified, defaults to '.gdb'

        self.m_gdbName = self.m_geodatabase[:len(self.m_geodatabase) - const_len_ext]       #.gdb
        self.m_geoPath = os.path.join(self.m_workspace, self.m_geodatabase)

        self.m_commands = self.getXMLNodeValue(self.m_doc, "Command")

        if (ext == self.const_geodatabase_SDE_ext):
            self.m_IsSDE = True
            try:
                self.log('Reading SDE connection properties from (%s)' % (self.m_geoPath))
                conProperties  = arcpy.Describe(self.m_geoPath).connectionProperties
                self.m_SDE_database_user = ('%s.%s.') % (conProperties.database, conProperties.user)

            except Exception as inst:
                self.log(str(inst), self.const_critical_text)
                return (False, self.const_init_ret_sde)

        return (True, 'OK')


    def setCodeBase(self, path):
        if (os.path.exists(path) == False):
            return None

        self.m_code_base = path

        self.const_statistics_path_ = os.path.join(self.m_code_base, '..\\..\\parameter\\Statistics')
        self.const_raster_function_templates_path_ = os.path.join(self.m_code_base, '..\\..\\parameter\\RasterFunctionTemplates')
        self.const_raster_type_path_ = os.path.join(self.m_code_base, '..\\..\\parameter\\Rastertype')
        self.const_workspace_path_ = os.path.join(self.m_code_base, '..\\..\\')      #.gdb output
        self.const_import_geometry_features_path_ = os.path.join(self.m_code_base, '..\\..\\parameter')

        return self.m_code_base


    def getXMLXPathValue(self, xPath, key):

        nodes = self.m_doc.getElementsByTagName(key)
        for node in nodes:
            parents = []
            c = node
            while(c.parentNode != None):
                parents.insert(0, c.nodeName)
                c = c.parentNode
            p = '/'.join(parents)
            if (p == xPath):
                if (node.hasChildNodes() == False):
                    return ''
                return str(node.firstChild.data).strip()

        return ''

    def setLog(self, log):
        self.m_log = log
        return True

    def isLog(self):
        return (not self.m_log == None)

    def log(self, msg, level = const_general_text):
        if (self.m_log != None):
            return self.m_log.Message(msg, level)

        errorTypeText = 'msg'
        if (level > self.const_general_text):
             errorTypeText = 'warning'
        elif(level == self.const_critical_text):
             errorTypeText = 'critical'

        print ('log-' + errorTypeText + ': ' + msg)

        return True


# user defined functions implementation code
    def isUser_Function(self, name):
        try:
            frame = sys._getframe(0).f_globals

            module = frame[self.CMODULE_NAME]
            cls = getattr(module, self.CCLASS_NAME)
            instance = cls()
            fnc = getattr(instance, name)
        except:
            return False

        return True


    def invoke_user_function(self, name, data):       # MDCS is always passed on which is the MD Configuration Script XML DOM
        ret = False
        try:
            frame = sys._getframe(0).f_globals  # default to first stack.

            module = frame[self.CMODULE_NAME]
            cls = getattr(module, self.CCLASS_NAME)
            instance = cls()
            fnc = getattr(instance, name)
            try:
                ret = fnc(data)
            except Exception as inf:
                self.log('Error: executing user defined function (%s)' % (name), self.const_critical_text)
                self.log(str(inf), self.const_critical_text)
                return False
        except Exception as inf:
            self.log('Error: please check if user function (%s) is found in class (%s) of MDCS_UC module.' % (name, CCLASS_NAME), self.const_critical_text)
            self.log(str(inf), self.const_critical_text)
            return False

        return ret
#ends


    def processEnv(self, node, pos, json):                #support fnc for 'SE' command.

        while(node.nextSibling != None):
            if(node.nodeType != minidom.Node.TEXT_NODE):

                k = str(pos)
                if ((k in json.keys()) == False):
                        json[k] = {'key' : [], 'val' : [], 'type' : [] }

                json[k]['key'].append(node.nodeName)
                v = ''
                if (node.firstChild != None):
                    v  = node.firstChild.nodeValue.strip()
                json[k]['val'].append(v)
                json[k]['parent'] = node.parentNode.nodeName
                json[k]['type'].append('c')

                if (node.firstChild != None):
                    if (node.firstChild.nextSibling != None):
                        pos = len(json)
                        json[k]['type'][len(json[k]['type']) - 1] = 'p'
                        self.processEnv(node.firstChild.nextSibling, pos, json)
                        pos = 0     # defaults to root always, assuming only 1 level deep xml.
            node = node.nextSibling

        return True


    def getAbsPath(self, input):
        absPath = input
        if (os.path.exists(absPath) == True):
            absPath = os.path.abspath(input)

        return absPath


    def prefixFolderPath(self, input, prefix):

        _file  = input.strip()
        _p, _f = os.path.split(_file)
        _indx = _p.lower().find('.gdb')
        if (_p == '' or _indx >= 0):
            if (_indx >= 0):
                _f   = _p + '\\' + _f
            _file = os.path.join(prefix, _f)

        return _file



    def isArcGISPatched(self):      # return values [true | false]

        # if we're running on python 3+, it's assumed we're on (ArcGIS Pro) and there's no need to check for patches.
        if (sys.version_info[0] >= 3):
            return True

        # if the patch XML node is not properly formatted in structure/with values, MDCS returns an error and will abort the operation.

        patch_node = self.getXMLNode(self.m_doc, "Patch")
        if (patch_node ==''):
            return True

        if (patch_node.attributes.length == 0):
            return False

        if ((self.CVERSION_ATTRIB in patch_node.attributes.keys()) == False):
            return False
        target_ver = patch_node.attributes.getNamedItem(self.CVERSION_ATTRIB).nodeValue.strip()
        if (len(target_ver) == 0):
            return False

        search_key = ''
        patch_desc_node = patch_node.firstChild.nextSibling
        while (patch_desc_node != None):
            node_name = patch_desc_node.nodeName
            if (node_name == 'Name'):
                if (patch_desc_node.hasChildNodes() == True):
                    search_key = patch_desc_node.firstChild.nodeValue
                    break
            patch_desc_node = patch_desc_node.nextSibling.nextSibling


        if (len(search_key) == 0):      # if no patch description could be found, return False
            return False

        ver = (target_ver + '.0.0.0.0').split('.')
        for n in range(self.CMAJOR, self.CBUILD + 1):
            if (ver[n] == ''):
                ver[n] = 0
            ver[n] = int(ver[n])
        ver = ver[:4]       # accept only the first 4 digits.

        target_v_str = installed_v_str = ''
        for i in range (self.CMAJOR, self.CBUILD + 1):
            target_v_str += "%04d" % ver[i]

        installed_ver = self.getDesktopVersion()
        for i in range (self.CMAJOR, self.CBUILD + 1):
            installed_v_str += "%04d" % installed_ver[i]


        tVersion = int(target_v_str)
        iVersion = int(installed_v_str)

        if (iVersion > tVersion):           # the first priority is to check for the patch version against the installed version
            return True                     # if the installed ArcGIS version is greater than the patch's, it's OK to proceed.

        # if the installed ArcGIS version is lower than the intended target patch version, continue with the registry key check for the
        # possible patches installed.
        #HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\ESRI\Desktop10.2\Updates

        CPRODUCT_NAME = 'ProductName'
        CVERSION = 'Version'

        setupInfo = arcpy.GetInstallInfo()
        if ((CVERSION in setupInfo.keys()) == False or
            (CPRODUCT_NAME in setupInfo.keys()) == False):
            return False

        key = setupInfo[CPRODUCT_NAME] + setupInfo[CVERSION]

        try:
            reg_path = "Software\\Wow6432Node\\ESRI\\%s\\Updates" % (key)
            arcgis = OpenKey(
                HKEY_LOCAL_MACHINE, reg_path)

            i = 0
            while 1:
                name = EnumKey(arcgis, i)
                arcgis_sub = OpenKey(
                    HKEY_LOCAL_MACHINE, reg_path + '\\' + name)
                try:
                    value, type = QueryValueEx(arcgis_sub, "Name")
                    if (type == 1):   # reg_sz
                        if (value.lower().find(search_key.lower()) >= 0):
                            return True     # return true if the value is found!
                except:
                    pass
                i += 1
        except:
            pass

        return False


    def getDesktopVersion(self):    #returns major, minor, sp and the build number.

        d = arcpy.GetInstallInfo()

        version = []

        buildNumber = 0
        spNumber = 0

        CVERSION = 'version'
        CBUILDNUMBER = 'buildnumber'
        CSPNUMBER = 'spnumber'

        ValError = False

        for k in d:
            key = k.lower()
            if (key == CVERSION or
                key == CBUILDNUMBER or
                key == CSPNUMBER):
                try:
                    if (key == CVERSION):
                        [version.append(int(x)) for x in d[k].split(".")]
                    elif (key == CBUILDNUMBER):
                        buildNumber = int(d[k])
                    elif (key == CSPNUMBER):
                        spNumber = int(d[k])        # could be N/A
                except:
                    ValError = True

        CMAJOR_MINOR_REVISION = 3
        if (len(version) < CMAJOR_MINOR_REVISION):  # On a system with full-install, ArcGIS version piece of information could return 3 numbers (major, minor, revision/SP)
            version.append(spNumber)                # and thus the SP number shouldn't be added to the version sperately.
        version.append(buildNumber)

        return version



    def CheckMDCSVersion(self, min, max, print_err_msg = True):

        # if python version is >= 3, it's asssumed we're being run from ArcGIS Pro
        if (sys.version_info[0] >= 3):
            min = [1, 0, 0, 0]
            max = [0, 0, 0, 0]

        if (len(min) != self.const_ver_len or
            len(max) != self.const_ver_len):
                return False

        CMAJOR = 0
        CMINOR = 1
        CSP = 2
        CBUILD = 3

        min_major = min[CMAJOR]
        min_minor = min[CMINOR]
        min_sp = min[CSP]
        min_build = min[CBUILD]

        max_major = max[CMAJOR]
        max_minor = max[CMINOR]
        max_cp = max[CSP]
        max_build = max[CBUILD]

        try:
            version = self.getDesktopVersion()
            if (len(version) >= self.const_ver_len): # major, minor, sp, build

                inst_major = version[CMAJOR]
                inst_minor = version[CMINOR]
                inst_sp = version[CSP]
                inst_build = version[CBUILD]

                ver_failed = False

                if (max_major > 0 and
                    inst_major > max_major):
                    ver_failed = True
                elif (max_minor > 0 and
                    inst_minor > max_minor):
                        ver_failed = True
                elif (max_cp > 0 and
                    inst_sp > max_cp):
                        ver_failed = True
                elif (max_build > 0 and
                      inst_build > max_build):
                            ver_failed = True
                elif (inst_major < min_major):
                    ver_failed = True
                elif (inst_minor < min_minor):
                        ver_failed = True
                elif (inst_sp < min_sp):
                        ver_failed = True
                elif (min_build > 0 and
                      inst_build < min_build):
                        ver_failed = True

                if (ver_failed):
                    if (print_err_msg == True):
                        self.log('MDCS can\'t proceed due to ArcGIS version incompatiblity.', self.const_critical_text)
                        self.log('ArcGIS Desktop version is (%s.%s.%s.%s). MDCS min and max versions are (%s.%s.%s.%s) and (%s.%s.%s.%s) respectively.' % \
                        (inst_major, inst_minor, inst_sp, inst_build, min_major, min_minor, min_sp, min_build, max_major, max_minor, max_cp, max_build), self.const_critical_text)

                    return False

        except Exception as inst:
            self.log('Version check failed: (%s)' % (str(inst)), self.const_critical_text)
            return False

        return True



    def getXMLNodeValue(self, doc, nodeName) :
        if (doc == None):
            return ''
        node = doc.getElementsByTagName(nodeName)

        if (node == None or
            node.length == 0 or
            node[0].hasChildNodes() == False or
            node[0].firstChild.nodeType != minidom.Node.TEXT_NODE):
            return ''

        return node[0].firstChild.data


    def updateART(self, doc, workspace, dataset):

        if (doc == None):
            return False

        if (workspace.strip() == ''
        and dataset.strip() == ''):
            return False        # nothing to do.

        try:
            nodeName = 'NameString'
            node_list = doc.getElementsByTagName(nodeName)

            for node in node_list:
                if (node.hasChildNodes() == True):
                    vals = node.firstChild.nodeValue.split(';')
                    upd_buff = []
                    for v in vals:
                        vs = v.split('=')
                        for vs_ in vs:
                            vs_ = vs_.lower()
                            if (vs_.find('workspace') > 0):
                                if (workspace != ''):
                                    vs[1] = ' ' + workspace
                                    if (node.nextSibling != None):
                                        if (node.nextSibling.nodeName == 'PathName'):
                                            node.nextSibling.firstChild.nodeValue = workspace

                            elif (vs_.find('rasterdataset') > 0):
                                if (dataset != ''):
                                    vs[1] = ' ' + dataset
                                    if (node.previousSibling != None):
                                        if (node.previousSibling.nodeName == 'Name'):
                                            node.previousSibling.firstChild.nodeValue = dataset
                        upd_buff.append('='.join(vs))

                    if (len(upd_buff) > 0):
                        upd_nodeValue = ';'.join(upd_buff)
                        node.firstChild.nodeValue = upd_nodeValue


            nodeName = 'ConnectionProperties'
            node_list = doc.getElementsByTagName(nodeName)
            found = False
            for node in node_list:      # only one node should exist.
                for n in node.firstChild.childNodes:
                    if (n.firstChild != None):
                        if (n.firstChild.firstChild != None):
                            if (n.firstChild.nodeName.lower() == 'key'):
                                if (n.firstChild.firstChild.nodeValue.lower() == 'database'):
                                    n.firstChild.nextSibling.firstChild.nodeValue  = workspace
                                    found = True
                                    break;

                if (found == True):
                    break


        except Exception as inst:
            self.log(str(inst), self.const_critical_text)
            return False

        return True




    def getInternalPropValue(self, dic, key):
        if (key in dic.keys()):
            return dic[key]
        else:
            return ''


    def setUserDefinedValues(self):

        nodes = self.m_doc.getElementsByTagName('*')
        for node in nodes:
            if (node.firstChild != None):
                 v = node.firstChild.data.strip()

                 if (v.find('$') == -1):
                    continue

                 usr_key = v
                 default = ''

                 d = v.split(';')

                 if (len(d) > 1):
                    default = d[0].strip()
                    usr_key = d[1].strip()

                 revalue = []

                 first = usr_key.find('$')
                 first += 1

                 second =  first + usr_key[first+1:].find('$') + 1

                 if (first > 1):
                    revalue.append(usr_key[0:first - 1])

                 while(second >= 0):

                    uValue = usr_key[first:second]

                    if (uValue.upper() in self.m_dynamic_params.keys()):
                        revalue.append(self.m_dynamic_params[uValue.upper()])
                    else:
                        if (uValue.find('\$') >= 0):
                            uValue = uValue.replace('\$', '$')
                        else:
                            if (default == ''):
                                default = uValue

                            if (first == 1
                            and second == (len(usr_key) - 1)):
                                uValue = default

                        revalue.append(uValue)

                    first = second + 1
                    indx = usr_key[first+1:].find('$')
                    if (indx == -1):
                        if (first != len(usr_key)):
                            revalue.append(usr_key[first:len(usr_key)])
                        break

                    second = first + indx + 1

                 updateVal = ''.join(revalue)
                 node.firstChild.data = updateVal



    def getXMLNode(self, doc, nodeName) :
        if (doc == None):
            return ''
        node = doc.getElementsByTagName(nodeName)

        if (node == None or
            node.length == 0 or
            node[0].hasChildNodes() == False or
            node[0].firstChild.nodeType != minidom.Node.TEXT_NODE):
            return ''

        return node[0]

    def foundLockFiles(self, folder_path):

        file_list_ = os.listdir(folder_path)
        found_lock_ = False
        for i in file_list_:
            if (i[-5:].lower() == '.lock'):
                sp = i.split('.')
                pid = os.getpid()
                if (pid == int(sp[3])):         #indx 3 == process id
                    found_lock_ = True
                    break;

        return found_lock_


    def waitForLockRelease(self, folder_path_):

        if (os.path.exists(folder_path_) == False):
            self.log('lock file path does not exist!. Quitting...', self.const_critical_text)
            return -2       #path does not exist error code!

        t0 = datetime.now()
        duration_req_sec_ = 3
        max_time_to_wait_sec_ = 10
        tot_count_sec_ = 0

        while True:
            if (tot_count_sec_ == 0):
                if (self.foundLockFiles(folder_path_) == False):   #try to see if we could get lucky on the first try, else enter periodic check.
                    break;
            t1 = datetime.now() - t0

            if (t1.seconds > duration_req_sec_):
                if (self.foundLockFiles(folder_path_) == False):
                    break;
                tot_count_sec_ += duration_req_sec_
                if (tot_count_sec_ > max_time_to_wait_sec_):
                    self.log('lock file release timed out!. Quitting...', self.const_critical_text)
                    tot_count_sec_ = -1
                    break;
                t0 = datetime.now()

        return tot_count_sec_


