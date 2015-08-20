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
# Name: SolutionsLib.py
# Description: To map MDCS command codes to GP Tool functions.
# Version: 20150422
# Requirements: ArcGIS 10.1 SP1
# Author: Esri Imagery Workflows team
#------------------------------------------------------------------------------
#!/usr/bin/env python

import arcpy
import sys, os
from xml.dom import minidom
from string import ascii_letters, digits

scriptPath = os.path.dirname(__file__)
sys.path.append(os.path.join(scriptPath, 'Base'))

import Base


class Solutions(Base.Base):

    processInfo = None
    userInfo = None
    config = ''
    m_base = None

    def __init__(self, base=None):
        if (base != None):
            self.setLog(base.m_log)
        self.m_base = base

        self.processInfo = None
        self.userInfo = None
        self.config = ''


    def getAvailableCommands(self):
        return self.commands


    def __invokeDynamicFnCallback(self, args, fn_name = None):
        if (fn_name == None):
            return args
        fn = fn_name.lower()
        if (fn == 'arcpy.exportmosaicdatasetitems_management'):
            try:
                CONST_OUTPUT_FOLDER_INDX = 1
                get_output_folder = args[CONST_OUTPUT_FOLDER_INDX] # let's create the output folder before invoking the function call.
                os.makedirs(get_output_folder)
            except:
                pass    # pass onto default error handler.
        elif(fn == 'arcpy.stageservice_server'):
            try:
                CONST_OUT_SRV_INDX = 1
                if (os.path.exists(args[CONST_OUT_SRV_INDX])):
                    os.remove(args[CONST_OUT_SRV_INDX])
            except:
                pass
        return args

    def __invokeDynamicFn(self, args, processKey, fn_name, index):
        try:
            varnames = eval('%s.__code__.co_varnames' % (fn_name))
            varcount = eval('%s.__code__.co_argcount' % (fn_name))
            varnames = varnames[:varcount]
            for i in range(len(args), len(varnames)):
                args.append(self.getProcessInfoValue(processKey, varnames[i].lower(), index))
            for i in range(0, len(varnames)):
                if (args[i] == '#'):    # the default marker (#) as returned by (getProcessInfoValue) gets replaced with (None)
                    args[i] = None
            setExportMosaicDatasetGeometry = Base.DynaInvoke(fn_name, args, self.__invokeDynamicFnCallback, self.m_log.Message)
            if (setExportMosaicDatasetGeometry.init() == False):
                return False
            return setExportMosaicDatasetGeometry.invoke()
        except:
            self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
            return False


    #mapping commands to functions
    def executeCommand(self, com, index = 0):

    #create the geodatabse to hold all relevant mosaic datasets.
        if (com == 'CM'):
            createMD = self.CreateMD.CreateMD(self.m_base)
            bSuccess = createMD.init(self.config)
            if (bSuccess):
                bSuccess = createMD.createGeodataBase()
                return createMD.createMD()
            return False

    #Add custom fields to elevation mosaic datasets.
        elif (com == 'AF'):
            addFields = self.AddFields.AddFields(self.m_base)
            bSuccess = addFields.init(self.config)
            if (bSuccess):
                return addFields.CreateFields()
            return False

    #Add rasters/data to mosaic datasets.
        elif (com == 'AR'):
            addRasters = self.AddRasters.AddRasters(self.m_base)
            bSuccess = addRasters.init(self.config)
            if (bSuccess):
                if (com in self.userInfo.keys()):
                    if ('cb' in self.userInfo[com].keys()):
                        bSuccess = addRasters.AddCallBack(self.userInfo[com]['cb'])
                return addRasters.AddRasters()
            return False

    #Create referenced mosaic datasets.
        elif(com == 'CR'):
            createRefMD = self.CreateRefMD.CreateReferencedMD(self.m_base)
            bSuccess = createRefMD.init(self.config)
            if (bSuccess):
                return createRefMD.createReferencedMD()
            return False

        elif(com == 'SP'):
            setProps = self.SetMDProperties.SetMDProperties(self.m_base)
            bSuccess = setProps.init(self.config)
            if (bSuccess):
                path = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                return setProps.setMDProperties(path)
            return False

        elif (com == 'CBMD'):
            try:
                self.m_log.Message("\tColor Balancing mosaic dataset : " + self.m_base.m_mdName, self.m_log.const_general_text)
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                processKey = 'colorbalancemosaicdataset'
                arcpy.ColorBalanceMosaicDataset_management(fullPath,
                self.getProcessInfoValue(processKey,'balancing_method', index),
                self.getProcessInfoValue(processKey,'color_surface_type', index),
                self.getProcessInfoValue(processKey,'target_raster', index),
                self.getProcessInfoValue(processKey,'exclude_raster', index),
                self.getProcessInfoValue(processKey,'stretch_type', index),
                self.getProcessInfoValue(processKey,'gamma', index),
                self.getProcessInfoValue(processKey,'block_field', index)
                )
                return True
            except:
                self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                return False

    #Remove Index from Mosaic dataset.
        elif (com == 'RI'):
            fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
            processKey = 'removeindex'
            try:
                self.log ("Removing Index(%s) " % (self.getProcessInfoValue(processKey, 'index_name', index)))
                arcpy.RemoveIndex_management(fullPath,
                self.getProcessInfoValue(processKey, 'index_name', index)
                )
                self.log(arcpy.GetMessages())
                return True
            except:
                self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                return False

    #Remove raster/Items from Mosaic dataset.
        elif (com == 'RRFMD'):
            try:
                self.m_log.Message("\tRemove rasters from mosaic dataset : " + self.m_base.m_mdName, self.m_log.const_general_text)
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                processKey = 'removerastersfrommosaicdataset'
                arcpy.RemoveRastersFromMosaicDataset_management(fullPath,
                self.getProcessInfoValue(processKey,'where_clause', index),
                self.getProcessInfoValue(processKey,'update_boundary', index),
                self.getProcessInfoValue(processKey,'mark_overviews_items', index),
                self.getProcessInfoValue(processKey,'delete_overview_images', index),
                self.getProcessInfoValue(processKey,'delete_item_cache', index),
                self.getProcessInfoValue(processKey,'remove_items', index),
                self.getProcessInfoValue(processKey,'update_cellsize_ranges', index)
                )
                return True
            except:
                self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                return False

    # Delete mosaic dataset.
        elif (com == 'DMD'):
            try:
                self.m_log.Message("\tDelete Mosaic dataset  : " + self.m_base.m_mdName, self.m_log.const_general_text)
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                processKey = 'deletemosaicdataset'
                arcpy.DeleteMosaicDataset_management(fullPath,
                self.getProcessInfoValue(processKey,'delete_overview_images', index),
                self.getProcessInfoValue(processKey,'delete_item_cache', index)
                )
                return True
            except:
                self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                return False

    # Merge mosaic dataset
        elif (com == 'MMDI'):
            try:
                self.m_log.Message("\tMerge mosaic dataset  Items: " + self.m_base.m_mdName, self.m_log.const_general_text)
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                processKey = 'mergemosaicdatasetitems'
                arcpy.MergeMosaicDatasetItems_management (fullPath,
                self.getProcessInfoValue(processKey,'where_clause', index),
                self.getProcessInfoValue(processKey,'block_field', index),
                self.getProcessInfoValue(processKey,'max_rows_per_merged_items', index)
                )
                return True
            except:
                self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                return False


        elif (com == 'ERF'):
            try:
                self.m_log.Message("\tEditing raster function : " + self.m_base.m_mdName, self.m_log.const_general_text)
                processKey = 'editrasterfunction'
                rfunction_path = self.getProcessInfoValue(processKey,'function_chain_definition', index)
                if (rfunction_path.find('.rft') >-1 and rfunction_path.find('/') == -1):
                    rfunction_path = self.m_base.const_raster_function_templates_path_ + "/" + rfunction_path

                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)

                lyrName = 'lyr_%s' % str(self.m_base.m_last_AT_ObjectID)
                expression = "OBJECTID >%s" % (str(self.m_base.m_last_AT_ObjectID))
                arcpy.MakeMosaicLayer_management(fullPath, lyrName, expression)

                arcpy.EditRasterFunction_management(lyrName,
                self.getProcessInfoValue(processKey,'edit_mosaic_dataset_item', index),
                self.getProcessInfoValue(processKey,'edit_options', index),
                rfunction_path,
                self.getProcessInfoValue(processKey,'location_function_name', index),
                )

                arcpy.Delete_management(lyrName)

                return True
            except:
                self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                return False

        elif (com == 'CS'):
            try:
                self.m_log.Message("\tCalculate statistic for the mosaic dataset : " + self.m_base.m_mdName, self.m_log.const_general_text)
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                processKey = 'calculatestatistics'
                arcpy.CalculateStatistics_management(fullPath,
                self.getProcessInfoValue(processKey,'x_skip_factor', index),
                self.getProcessInfoValue(processKey,'y_skip_factor', index),
                self.getProcessInfoValue(processKey,'ignore_values', index),
                self.getProcessInfoValue(processKey,'skip_existing', index),
                self.getProcessInfoValue(processKey,'area_of_interest', index)
                )
                return True
            except:
                self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                return False

        elif (com == 'BPS'):
            try:
                self.m_log.Message("\tBuilding Pyramids and Calculating Statistic for the mosaic dataset : " + self.m_base.m_mdName, self.m_log.const_general_text)
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                processKey = 'buildpyramidsandstatistics'

                lyrName = 'lyr_%s' % str(self.m_base.m_last_AT_ObjectID)
                expression = "OBJECTID >%s" % (str(self.m_base.m_last_AT_ObjectID))
                arcpy.MakeMosaicLayer_management(fullPath, lyrName, expression)

                arcpy.BuildPyramidsandStatistics_management(lyrName,
                self.getProcessInfoValue(processKey,'include_subdirectories', index),
                self.getProcessInfoValue(processKey,'build_pyramids', index),
                self.getProcessInfoValue(processKey,'calculate_statistics', index),
                self.getProcessInfoValue(processKey,'BUILD_ON_SOURCE', index),
                self.getProcessInfoValue(processKey,'block_field', index),
                self.getProcessInfoValue(processKey,'estimate_statistics', index),
                self.getProcessInfoValue(processKey,'x_skip_factor', index),
                self.getProcessInfoValue(processKey,'y_skip_factor', index),
                self.getProcessInfoValue(processKey,'ignore_values', index),
                self.getProcessInfoValue(processKey,'pyramid_level', index),
                self.getProcessInfoValue(processKey,'SKIP_FIRST', index),
                self.getProcessInfoValue(processKey,'resample_technique', index),
                self.getProcessInfoValue(processKey,'compression_type', index),
                self.getProcessInfoValue(processKey,'compression_quality', index),
                self.getProcessInfoValue(processKey,'skip_existing', index)
                )

                arcpy.Delete_management(lyrName)

                return True
            except:
                self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                return False

        elif(com == 'BP'):
            try:
                self.m_log.Message("\tBuilding Pyramid for the mosaic dataset/raster dataset : " + self.m_base.m_mdName, self.m_log.const_general_text)
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                processKey = 'buildpyramids'
                arcpy.BuildPyramids_management(fullPath,
                self.getProcessInfoValue(processKey,'pyramid_level', index),
                self.getProcessInfoValue(processKey,'SKIP_FIRST', index),
                self.getProcessInfoValue(processKey,'resample_technique', index),
                self.getProcessInfoValue(processKey,'compression_type', index),
                self.getProcessInfoValue(processKey,'compression_quality', index),
                self.getProcessInfoValue(processKey,'skip_existing', index))
                return True
            except:
                self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                return False

        elif(com == 'BF'):
                try:
                    self.m_log.Message("\tRecomputing footprint for the mosaic dataset: " + self.m_base.m_mdName, self.m_log.const_general_text)
                    fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)

                    processKey = 'buildfootprint'

                    isQuery = False
                    query = self.getProcessInfoValue(processKey, 'where_clause', index)
                    if (len(query) > 0 and
                        query != '#'):
                            isQuery = True

                    expression = "OBJECTID >%s" % (str(self.m_base.m_last_AT_ObjectID))
                    if (isQuery == True):
                        expression += ' AND %s' % (query)

                    args = []
                    args.append(fullPath)
                    args.append(expression)
                    args.append(self.getProcessInfoValue(processKey, 'reset_footprint', index))
                    args.append(self.getProcessInfoValue(processKey, 'min_data_value', index))
                    args.append(self.getProcessInfoValue(processKey, 'max_data_value', index))
                    args.append(self.getProcessInfoValue(processKey, 'approx_num_vertices', index))
                    args.append(self.getProcessInfoValue(processKey, 'shrink_distance', index))
                    args.append(self.getProcessInfoValue(processKey, 'maintain_edges', index))
                    args.append(self.getProcessInfoValue(processKey, 'skip_derived_images', index))
                    args.append(self.getProcessInfoValue(processKey, 'update_boundary', index))
                    args.append(self.getProcessInfoValue(processKey, 'request_size', index))
                    args.append(self.getProcessInfoValue(processKey, 'min_region_size', index))
                    args.append(self.getProcessInfoValue(processKey, 'simplification_method', index))
                    args.append(self.getProcessInfoValue(processKey, 'edge_tolerance', index))
                    args.append(self.getProcessInfoValue(processKey, 'max_sliver_size', index))
                    args.append(self.getProcessInfoValue(processKey, 'min_thinness_ratio', index))

                    setBuitFootprints = Base.DynaInvoke('arcpy.BuildFootprints_management', args, None, self.m_log.Message)
                    if (setBuitFootprints.init() == False):
                        return False
                    return setBuitFootprints.invoke()
                except:
                    self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                    return False

        elif (com == 'BS'):
                try:
                    self.m_log.Message("\tBuild Seamline for the mosaic dataset: " + self.m_base.m_mdName, self.m_log.const_general_text)
                    fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                    processKey = 'buildseamlines'
                    args = []
                    args.append(fullPath)
                    args.append(self.getProcessInfoValue(processKey,'cell_size', index))
                    args.append(self.getProcessInfoValue(processKey,'sort_method', index))
                    args.append(self.getProcessInfoValue(processKey,'sort_order', index))
                    args.append(self.getProcessInfoValue(processKey,'order_by_attribute', index))
                    args.append(self.getProcessInfoValue(processKey,'order_by_base_value', index))
                    args.append(self.getProcessInfoValue(processKey,'view_point', index))
                    args.append(self.getProcessInfoValue(processKey,'computation_method', index))
                    args.append(self.getProcessInfoValue(processKey,'blend_width', index))
                    args.append(self.getProcessInfoValue(processKey,'blend_type', index))
                    args.append(self.getProcessInfoValue(processKey,'request_size', index))
                    args.append(self.getProcessInfoValue(processKey,'request_size_type', index))
                    args.append(self.getProcessInfoValue(processKey,'blend_width_units', index))
                    args.append(self.getProcessInfoValue(processKey,'area_of_interest', index))
                    args.append(self.getProcessInfoValue(processKey,'where_clause', index))
                    args.append(self.getProcessInfoValue(processKey,'update_existing', index))

                    setBuitSeamlines = Base.DynaInvoke('arcpy.BuildSeamlines_management', args, None, self.m_log.Message)
                    if (setBuitSeamlines.init() == False):
                        return False
                    return setBuitSeamlines.invoke()
                except:
                    self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                    return False

        elif (com == 'EMDG'):
                    self.m_log.Message("\tExport mosaic dataset geometry:" + self.m_base.m_mdName, self.m_log.const_general_text)
                    fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                    return self.__invokeDynamicFn(
                    [fullPath],
                    'exportmosaicdatasetgeometry',
                    'arcpy.ExportMosaicDatasetGeometry_management',
                    index
                    )

        elif (com == 'EMDI'):
                    self.m_log.Message("\tExport mosaic dataset items:" + self.m_base.m_mdName, self.m_log.const_general_text)
                    fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                    return self.__invokeDynamicFn(
                    [fullPath],
                    'exportmosaicdatasetitems',
                    'arcpy.ExportMosaicDatasetItems_management',
                    index
                    )

        elif (com == 'SMDI'):
                    self.m_log.Message("\tSplit mosaic dataset items:" + self.m_base.m_mdName, self.m_log.const_general_text)
                    fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                    return self.__invokeDynamicFn(
                    [fullPath],
                    'splitmosaicdatasetitems',
                    'arcpy.MergeMosaicDatasetItems_management',
                    index
                    )

        elif (com == 'SY'):
                    self.m_log.Message("\tSynchronize mosaic dataset:" + self.m_base.m_mdName, self.m_log.const_general_text)
                    fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                    return self.__invokeDynamicFn(
                    [fullPath],
                    'synchronizemosaicdataset',
                    'arcpy.SynchronizeMosaicDataset_management',
                    index
                    )

        elif (com == 'CSDD'):
                    self.m_log.Message("\t{}:{}".format(self.commands[com]['desc'], self.m_base.m_mdName), self.m_log.const_general_text)
                    fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                    return self.__invokeDynamicFn(
                    [fullPath],
                    'createimagesddraft',
                    'arcpy.CreateImageSDDraft',
                    index
                    )

        elif (com == 'STS'):
                    self.m_log.Message("\t{}:{}".format(self.commands[com]['desc'], self.m_base.m_mdName), self.m_log.const_general_text)
                    return self.__invokeDynamicFn(
                    [],
                    'stageservice_server',
                    'arcpy.StageService_server',
                    index
                    )

        elif (com == 'USD'):
                    self.m_log.Message("\t{}".format(self.commands[com]['desc']), self.m_log.const_general_text)
                    return self.__invokeDynamicFn(
                    [],
                    'uploadservicedefinition_server',
                    'arcpy.UploadServiceDefinition_server',
                    index
                    )

        elif(com =='JF'):
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                try:
                    processKey ='joinfield'
                    arcpy.JoinField_management(self.getProcessInfoValue(processKey, 'in_data', index),
                    self.getProcessInfoValue(processKey, 'in_field', index),
                    self.getProcessInfoValue(processKey, 'join_table', index),
                    self.getProcessInfoValue(processKey, 'join_field', index),
                    self.getProcessInfoValue(processKey, 'fields', index))
                    return True
                except:
                    self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                    return False

        elif(com == 'DN'):
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                try:
                    processKey = 'definemosaicdatasetnodata'

                    lyrName = 'lyr_%s' % str(self.m_base.m_last_AT_ObjectID)
                    expression = "OBJECTID >%s" % (str(self.m_base.m_last_AT_ObjectID))
                    arcpy.MakeMosaicLayer_management(fullPath, lyrName, expression)

                    arcpy.DefineMosaicDatasetNoData_management(
                    lyrName,
                    self.getProcessInfoValue(processKey, 'num_bands', index),
                    self.getProcessInfoValue(processKey, 'bands_for_nodata_value', index),
                    self.getProcessInfoValue(processKey, 'bands_for_valid_data_range', index),
                    self.getProcessInfoValue(processKey, 'where_clause', index),
                    self.getProcessInfoValue(processKey, 'composite_nodata_value', index)
                    )
                    arcpy.Delete_management(lyrName)
                    return True

                except:
                    self.log(arcpy.GetMessages(), self.m_log.const_critical_text)

        elif(com == 'IG'):
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                try:
                    processKey = 'importgeometry'
                    importPath = self.getProcessInfoValue(processKey, 'input_featureclass', index)
                    const_ig_search_ = '.gdb\\'
                    igIndx = importPath.lower().find(const_ig_search_)
                    igIndxSep = importPath.find('\\')

                    if (igIndxSep == igIndx + len(const_ig_search_) - 1):
                        importPath = self.prefixFolderPath(importPath, self.m_base.const_import_geometry_features_path_)

                    arcpy.ImportMosaicDatasetGeometry_management(
                    fullPath,
                    self.getProcessInfoValue(processKey, 'target_featureclass_type', index),
                    self.getProcessInfoValue(processKey, 'target_join_field', index),
                    importPath,
                    self.getProcessInfoValue(processKey, 'input_join_field', index)
                    )
                    return True
                except:
                    self.log(arcpy.GetMessages(), self.m_log.const_critical_text)

        elif(com == 'IF'):
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                processKey = 'importfieldvalues'

                try:
                    j = 0
                    joinTable = self.getProcessInfoValue(processKey, 'input_featureclass', index)
                    confTableName = os.path.basename(joinTable)

                    joinFeildList = [f.name for f in arcpy.ListFields(joinTable)]
                    self.log(joinFeildList)
                    mlayer = os.path.basename(fullPath) +"layer" + str(j)
                    j = j + 1
                    arcpy.MakeMosaicLayer_management(fullPath,mlayer)
                    self.log("Joining the mosaic dataset layer with the configuration table", self.m_log.const_general_text)
                    mlayerJoin = arcpy.AddJoin_management(
                    mlayer + "/Footprint",
                    self.getProcessInfoValue(processKey, 'input_join_field', index),
                    joinTable,
                    self.getProcessInfoValue(processKey, 'target_join_field', index),
                    "KEEP_ALL"
                    )
                    for jfl in joinFeildList:
                        if jfl == "Comments" or jfl == "OBJECTID" or jfl == "Dataset_ID":
                            self.log("\t\tvalues exist for the field : " + jfl, self.m_log.const_general_text)
                        else:
                            fieldcal ="AMD_" + mdName + "_CAT." + jfl
                            fromfield = "["+confTableName+"." + jfl + "]"
                            try:
                                arcpy.CalculateField_management(mlayerJoin,fieldcal,fromfield)
                                self.log("\t\tDone calculating values for the Field :" + fieldcal, self.m_log.const_general_text)
                            except:
                                self.log("Failed to calculate values for the field : " + fieldcal, self.m_log.const_warning_text)
                                self.log(arcpy.GetMessages(), self.m_log.const_warning_text)
                    return True
                except:
                    self.log(arcpy.GetMessages(), self.m_log.const_critical_text)


        elif(com == 'BB'):
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                processKey = 'buildboundary'
                self.log ("Building the boundary "+ self.getProcessInfoValue(processKey, 'simplification_method', index))
                try:
                    arcpy.BuildBoundary_management(
                    fullPath,
                    self.getProcessInfoValue(processKey, 'where_clause', index),
                    self.getProcessInfoValue(processKey, 'append_to_existing', index),
                    self.getProcessInfoValue(processKey, 'simplification_method', index)
                    )
                    return True
                except:
                    self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                    return False

        # Delete fields
        elif(com == 'DF'):
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                processKey = 'deletefield'
                try:
                    self.log ("Deleting fields (%s) " % (self.getProcessInfoValue(processKey, 'drop_field', index)))

                    arcpy.DeleteField_management(
                    fullPath,
                    self.getProcessInfoValue(processKey, 'drop_field', index)
                    )
                    self.log(arcpy.GetMessages())
                    return True
                except:
                    self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                    return False

        elif(com == 'RP'):
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                processKey = 'repairmosaicdatasetpaths'
                self.log ("Repairing mosaic dataset paths ")
                try:
                    arcpy.RepairMosaicDatasetPaths_management(
                    fullPath,
                    self.getProcessInfoValue(processKey, 'paths_list', index),
                    self.getProcessInfoValue(processKey, 'where_clause', index)
                    )
                    return True
                except:
                    self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                    return False

        elif(com == 'SS'):
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                processKey = 'setstatistics'
                self.log("Setting MD statistics for:" + fullPath, self.m_log.const_general_text)
                stats_file_ss = self.m_base.getAbsPath(self.getProcessInfoValue(processKey, 'stats_file', index))
                if stats_file_ss != '#' and stats_file_ss != '' :
                    stats_file_ss = self.prefixFolderPath(self.getProcessInfoValue(processKey, 'stats_file', index), self.m_base.const_statistics_path_)

                try:
                    arcpy.SetRasterProperties_management(
                    fullPath,
                    self.getProcessInfoValue(processKey, 'data_type', index),
                    self.getProcessInfoValue(processKey, 'statistics', index),
                    stats_file_ss,
                    self.getProcessInfoValue(processKey, 'nodata', index)
                     )
                    return True
                except:
                    self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                    return False

        elif(com == 'CC'):
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                processKey = 'calculatecellsizeranges'
                self.log("Calculating cell ranges for:" + fullPath, self.m_log.const_general_text)

                try:
                    arcpy.CalculateCellSizeRanges_management(
                    fullPath,
                    self.getProcessInfoValue(processKey, 'where_clause', index),
                    self.getProcessInfoValue(processKey, 'do_compute_min', index),
                    self.getProcessInfoValue(processKey, 'do_compute_max', index),
                    self.getProcessInfoValue(processKey, 'max_range_factor', index),
                    self.getProcessInfoValue(processKey, 'cell_size_tolerance_factor', index),
                    self.getProcessInfoValue(processKey, 'update_missing_only', index),
                     )
                    return True
                except:
                    self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                    return False

        elif(com == 'BO'):
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                processKey = 'buildoverviews'
                self.log("Building overviews for:" + fullPath, self.m_log.const_general_text)

                try:
                    arcpy.BuildOverviews_management(
                    fullPath,
                    self.getProcessInfoValue(processKey, 'where_clause', index),
                    self.getProcessInfoValue(processKey, 'define_missing_tiles', index),
                    self.getProcessInfoValue(processKey, 'generate_overviews', index),
                    self.getProcessInfoValue(processKey, 'generate_missing_images', index),
                    self.getProcessInfoValue(processKey, 'regenerate_stale_images', index)
                     )
                    return True
                except:
                    self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                    return False

        elif(com == 'DO'):
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                processKey = 'defineoverviews'
                self.log("Define overviews for:" + fullPath, self.m_log.const_general_text)

                try:
                    arcpy.DefineOverviews_management(
                    fullPath,
                    self.getProcessInfoValue(processKey, 'overview_image_folder', index),
                    self.getProcessInfoValue(processKey, 'in_template_dataset', index),
                    self.getProcessInfoValue(processKey, 'extent', index),
                    self.getProcessInfoValue(processKey, 'pixel_size', index),
                    self.getProcessInfoValue(processKey, 'number_of_levels', index),
                    self.getProcessInfoValue(processKey, 'tile_rows', index),
                    self.getProcessInfoValue(processKey, 'tile_cols', index),
                    self.getProcessInfoValue(processKey, 'overview_factor', index),
                    self.getProcessInfoValue(processKey, 'force_overview_tiles', index),
                    self.getProcessInfoValue(processKey, 'resampling_method', index),
                    self.getProcessInfoValue(processKey, 'compression_method', index),
                    self.getProcessInfoValue(processKey, 'compression_quality', index)
                     )
                    return True
                except:
                    self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                    return False

        elif(com == 'AI'):
                fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                processKey = 'addindex'
                self.log("Adding Index:" + fullPath, self.m_log.const_general_text)

                maxValues = len(self.processInfo.processInfo[processKey][index])
                isError = False
                for indx in range(0, maxValues):

                    try:
                        arcpy.AddIndex_management(fullPath,
                        self.getProcessInfoValue(processKey, 'fields', index, indx),
                        self.getProcessInfoValue(processKey, 'index_name', index, indx),
                        self.getProcessInfoValue(processKey, 'unique', index, indx),
                        self.getProcessInfoValue(processKey, 'ascending', index, indx)
                        )
                    except:
                        self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                        isError = True

                return not isError


        elif(com == 'CFC'):
            fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
            processKey = 'cachefeatureclass'

            seamlineFC_name = 'AMD_' + self.m_base.m_mdName + '_SML'
            seamlineFC_Path = os.path.join(self.m_base.m_geoPath,seamlineFC_name)
            if (arcpy.Exists(seamlineFC_Path) == False):
                self.log("Seamline does not exist for the mosaic dataset: " + fullPath, self.m_log.const_general_text)
                return False

            try:
                outCFC = self.getProcessInfoValue(processKey, 'out_cache_featureclass', index).replace('\\', '/')
            except Exception as inf:
                self.log(str(inf), self.m_log.const_critical_text)
                return False

            if (outCFC.find('/') == -1):
                outCFC = os.path.join(self.m_base.m_geoPath, outCFC)

            if arcpy.Exists(outCFC):
                self.log("Output cache feature class already exists: " + outCFC, self.m_log.const_critical_text)
                return False

            (outCFC_wrk, outCFC_name) = os.path.split(outCFC)
            self.log("Exporting seamline as a feaure class: " + outCFC, self.m_log.const_general_text)

            try:
                arcpy.FeatureClassToFeatureClass_conversion(seamlineFC_Path, outCFC_wrk, outCFC_name, "#", "#", "#")
            except:
                self.log('Failed to create the output featue class (%s): (%s)' % (outCFC, arcpy.GetMessages()), self.m_log.const_critical_text)
                return False
            try:
                dropFList = ['BlendWidthUnits', 'BlendType', 'BlendWidth', 'ItemHash']
                sfieldList = arcpy.ListFields(seamlineFC_Path)
                for sfield in sfieldList:
                    if sfield.name.lower() in dropFList:
                        dropFList.remove(sfield.name)

                arcpy.DeleteField_management(outCFC, dropFList)
            except:
                self.log('Failed to delete the fields: ' + arcpy.GetMessages(), self.m_log.const_critical_text)

            catfieldList= []
            catfield = arcpy.ListFields(fullPath)
            for field in catfield:
                catfieldList.append(field.name)
            removelist = [u'OBJECTID', u'Shape', u'Raster',u'MinPS', u'MaxPS', u'HighPS', u'Category', u'Tag', u'GroupName', u'ProductName', u'CenterX', u'CenterY', u'ZOrder', u'TypeID', u'ItemTS', u'UriHash', u'Uri', u'Shape_Length', u'Shape_Area', u'SOrder', u'SLevelPS']
            importField = list(set(catfieldList) - set(removelist))

            try:
                arcpy.JoinField_management(outCFC, "RasterID", fullPath, "OBJECTID", importField)
            except:
                self.log("Failed to import metadata fields:" + arcpy.GetMessages(), self.m_log.const_critical_text)
                return False

            return True

        elif(com == 'CV'):
                    fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                    processKey = 'calculatevalues'

                    max_CV = len(self.processInfo.processInfo[processKey])
                    if (index > max_CV - 1):
                        self.log('Wrong index (%s) specified for (%s). Max index is (%s)' % (index,  processKey, max_CV - 1), self.m_log.const_critical_text)
                        return False

                    fullPath = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
                    maxValues = len(self.processInfo.processInfo[processKey][index])
                    self.log("Calculate values:" + fullPath, self.m_log.const_general_text)
                    isError = False

                    for indx in range(0, maxValues):

                        isQuery = False
                        query = self.getProcessInfoValue(processKey, 'query', index, indx)
                        lyrName = 'lyr_%s' % str(self.m_base.m_last_AT_ObjectID)

                        if (query != '#'):
                            isQuery = True

                        expression = "OBJECTID >%s" % (str(self.m_base.m_last_AT_ObjectID))
                        if (isQuery == True):
                            expression += ' AND %s' % (query)
                        try:
                            arcpy.MakeMosaicLayer_management(fullPath, lyrName, expression)

                            arcpy.CalculateField_management(lyrName,
                            self.getProcessInfoValue(processKey, 'fieldname', index, indx),
                            self.getProcessInfoValue(processKey, 'expression', index, indx),
                            self.getProcessInfoValue(processKey, 'expression_type', index, indx),
                            self.getProcessInfoValue(processKey, 'code_block', index, indx)
                            )
                        except:
                            self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                            isError = True
                        try:
                            arcpy.Delete_management(lyrName)     # passes for unknown/uncreated layer names
                        except:
                            log.Message(arcpy.GetMessages(), log.const_warning_text)
                            isError = True

                    return not isError

        elif(com == 'CP'):
                self.log("Compacting file geodatabase:" + self.m_base.m_geoPath, self.m_log.const_general_text)

                try:
                    arcpy.Compact_management(self.m_base.m_geoPath)
                    return True
                except:
                    self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                    return False

        elif(com == 'SE'):
                self.log("Set environment variables on index: %s" % (index), self.m_log.const_general_text)

                node = self.m_base.m_doc.getElementsByTagName('Environment')
                if (len(node) == 0 or
                    index > len(node) - 1):
                    self.log('No environment variables could be found/at index (%s)' % (index), self.m_log.const_warning_text)
                    return False

                json = {}
                self.processEnv (node[index].firstChild, 0, json)

                for l in range(0, len(json)):
                    p = str(l)
                    pIndx = -1
                    parent = json[p]['parent'].lower()
                    if (parent == 'environment'):
                        pIndx = 0

                    key_ = val_ = ''
                    key_len_ = len(json[p]['key'])
                    for i in range(0, key_len_):
                        typ = json[p]['type'][i]
                        if (typ != 'p'):
                            try:
                                k = json[p]['key'][i]
                                v =  json[p]['val'][i]

                                if (k == 'ClearEnvironment' or      # no use for these yet.
                                    k ==  'ResetEnvironments'):
                                        continue

                                if (pIndx == 0):
                                    key_  =  k
                                    val_ =  v.strip()

                                    if (val_ != ''):
                                        arcpy.env[key_] = val_
                                        self.log('Env[%s]=%s' % (key_, val_), self.m_log.const_general_text)
                                    continue
                                else:
                                    key_ = json[p]['parent']

                                val_ += json[p]['val'][i]
                                if (i < key_len_ - 1):
                                    val_ += ' '
                                else:
                                    if (val_.strip() != ''):
                                        arcpy.env[key_] = val_
                                        self.log('Env[%s]=%s' % (key_, val_), self.m_log.const_general_text)

                            except Exception as inst:
                                self.log(str(inst), self.m_log.const_warning_text)
                                continue

                return True     #should unable to set environment variables return False?

        elif (com == 'MTC'):

            mdName = os.path.join(self.m_base.m_geoPath, self.m_base.m_mdName)
            processKey = 'managetilecache'
            self.log("Building cache for:" + mdName, self.m_log.const_general_text)

            try:
                arcpy.ManageTileCache_management(
                self.getProcessInfoValue(processKey, 'in_cache_location',index),
                self.getProcessInfoValue(processKey, 'manage_mode',index),
                self.getProcessInfoValue(processKey, 'in_cache_name',index),
                mdName,
                self.getProcessInfoValue(processKey, 'tiling_scheme',index),
                self.getProcessInfoValue(processKey, 'import_tiling_scheme',index),
                self.getProcessInfoValue(processKey,'scales',index),
                self.getProcessInfoValue(processKey,'area_of_interest',index),
                self.getProcessInfoValue(processKey, 'max_cell_size',index))

                return True
            except:
                self.log(arcpy.GetMessages(), self.m_log.const_critical_text)

        elif (com == 'ETC'):
            processKey = 'exporttilecache'
            try:
                self.log("Exporting cache for:" + self.getProcessInfoValue(processKey, 'in_target_cache_name',index), self.m_log.const_general_text)

                arcpy.ExportTileCache_management(
                self.getProcessInfoValue(processKey, 'in_cache_source',index),
                self.getProcessInfoValue(processKey, 'in_target_cache_folder',index),
                self.getProcessInfoValue(processKey, 'in_target_cache_name',index),
                self.getProcessInfoValue(processKey, 'export_cache_type',index),
                self.getProcessInfoValue(processKey, 'storage_format_type',index),
                self.getProcessInfoValue(processKey,'scales',index),
                self.getProcessInfoValue(processKey,'area_of_interest',index))

                return True
            except:
                self.log(arcpy.GetMessages(), self.m_log.const_critical_text)

        elif (com == 'STP'):
            processKey = 'sharepackage'
            try:
                self.log("Publishing Tile Package:" + self.getProcessInfoValue(processKey, 'in_package',index), self.m_log.const_general_text)

                arcpy.SharePackage_management (
                self.getProcessInfoValue(processKey, 'in_package',index),
                self.getProcessInfoValue(processKey, 'username',index),
                self.getProcessInfoValue(processKey, 'password',index),
                self.getProcessInfoValue(processKey, 'summary',index),
                self.getProcessInfoValue(processKey, 'tags',index),
                self.getProcessInfoValue(processKey, 'credits',index),
                self.getProcessInfoValue(processKey,'public',index),
                self.getProcessInfoValue(processKey, 'groups',index))

                return True
            except:
                self.log(arcpy.GetMessages(), self.m_log.const_critical_text)
                return False

        else:

            # The command could be a user defined function externally defined in the module (MDCS_UC.py). Let's invoke it.
            data = {
            'log' : self.m_log,
            'workspace' : self.m_base.m_geoPath,
            'mosaicdataset' : self.m_base.m_mdName,
            'mdcs' : self.m_base.m_doc
            }
            return self.invoke_user_function(com, data)

        return False            #main function body return, no matching command found!



    commands = \
    {
    'CM' :
        {   'desc' : 'Create a new mosaic dataset.',
            'fnc' : executeCommand
        },
    'CR' :
        {   'desc' : 'Create new referenced mosaic dataset.',
            'fnc' : executeCommand
        },
    'AF' :
        {   'desc' : 'Add fields.',
            'fnc' : executeCommand
        },
    'AR' :
        {   'desc' : 'Add rasters/data to a mosaic dataset.',
            'fnc' : executeCommand
        },
    'BF' :
        {   'desc' : 'Build footprint.',
            'fnc' : executeCommand
        },
    'JF' :
        {   'desc' : 'Join the content of two tables based on a common attribute field.',
            'fnc' : executeCommand
        },
    'BS' :
        {   'desc' : 'Build Seamlines.',
            'fnc' : executeCommand
        },
    'BP' :
        {   'desc' : 'Build Pyramid.',
            'fnc' : executeCommand
        },
    'CS' :
        {   'desc' : 'Calculate Statistics.',
            'fnc' : executeCommand
        },
    'RP' :
        {   'desc' : 'Repair mosaic dataset paths',
            'fnc' : executeCommand
        },
    'CBMD' :
        {   'desc' : 'Color balance mosaic dataset.',
            'fnc' : executeCommand
        },
    'RRFMD' :
        {   'desc' : 'Remove Rasters from Mosaic ataset.',
            'fnc' : executeCommand
        },
    'DMD' :
        {   'desc' : 'Delete Mosaic dataset.',
            'fnc' : executeCommand
        },
   'MMDI' :
        {   'desc' : 'Merge Mosaic dataset items.',
            'fnc' : executeCommand
        },
    'BPS' :
        {   'desc' : 'Build pyramid and Statistics.',
            'fnc' : executeCommand
        },
    'ERF' :
        {   'desc' : 'Edit raster function.',
            'fnc' : executeCommand
        },
    'DN' :
        {   'desc' : 'Define no data values.',
            'fnc' : executeCommand
        },
    'SP' :
        {   'desc' : 'Set mosaic dataset properties.',
            'fnc' : executeCommand
        },
    'IG' :
        {   'desc' : 'Import mosaic dataset geometry.',
            'fnc' : executeCommand
        },
    'DF' :
        {   'desc' : 'Delete field.',
            'fnc' : executeCommand
        },
    'IF' :
        {   'desc' : 'Import field values/calculate fields.',
            'fnc' : executeCommand
        },
    'BB' :
        {   'desc' : 'Build boundary.',
            'fnc' : executeCommand
        },
    'SS' :
        {   'desc' : 'Set statistics for a raster or mosaic dataset.',
            'fnc' : executeCommand
        },
    'CC' :
        {   'desc' : 'Computes the minimum and maximum cell sizes for the rasters in a mosaic dataset.',
            'fnc' : executeCommand
        },
    'BO' :
        {   'desc' : 'Defines and generates overviews for a mosaic dataset.',
            'fnc' : executeCommand
        },
    'DO' :
        {   'desc' : 'Defines the tiling schema and properties of the preprocessed raster datasets.',
            'fnc' : executeCommand
        },
    'AI' :
        {   'desc' : 'Adds attribute index on the mosaic dataset.',
            'fnc' : executeCommand
        },
    'RI' :
        {   'desc' : 'Removes attribute index on the mosaic dataset.',
            'fnc' : executeCommand
        },
    'CFC' :
        {   'desc' : 'Create cache feature class.',
            'fnc' : executeCommand
        },
    'CV' :
        {   'desc' : 'Calculate mosaic dataset values.',
            'fnc' : executeCommand
        },
    'CP' :
        {   'desc' : 'Compact file geodatabase.',
            'fnc' : executeCommand
        },
    'SY' :
        {   'desc' : 'Synchronize mosaic dataset.',
            'fnc' : executeCommand
        },
    'SE' :
        {   'desc' : 'Set environment variables.',
            'fnc' : executeCommand
        },
    'MTC' :
        {   'desc' : 'Manage Tile Cache.',
            'fnc' : executeCommand
        },
    'ETC' :
        {   'desc' : 'Export Tile Cache.',
            'fnc' : executeCommand
        },
    'STP' :
        {   'desc' : 'Share Package.',
            'fnc' : executeCommand
        },
    'EMDG' :
        {   'desc' : 'Export mosaic dataset geometry.',
            'fnc' : executeCommand
        },
    'EMDI' :
        {   'desc' : 'Export mosaic dataset items.',
            'fnc' : executeCommand
        },
    'SMDI' :
        {   'desc' : 'Split mosaic dataset items.',
            'fnc' : executeCommand
        },
    'CSDD' :
        {   'desc' : 'Create an image service definition draft file.',
            'fnc' : executeCommand
        },
    'STS' :
        {   'desc' : 'Stages a service definition.',
            'fnc' : executeCommand
        },
    'USD' :
        {   'desc' : 'Uploads and publishes a service definition to a specified server.',
            'fnc' : executeCommand
        }
    }


    #mapping of config/component paths.

    base_path_ = scriptPath + '\\'

    com_locations = \
    {
    'CreateMD' :
        {
            'pyc' : base_path_ + 'CreateMD',
        },
    'AddFields' :
        {
            'pyc' : base_path_ + 'AddFields/',
        },
    'AddRasters' :
        {
            'pyc' : base_path_ + 'AddRasters/',
        },
    'SetMDProperties' :
        {
            'pyc' : base_path_ + 'SetMDProperties/',
        },
    'CreateRefMD' :
        {
            'pyc' : base_path_ + 'CreateRefMD/',
        },
    'ProcessInfo' :
        {
            'pyc' : base_path_ + 'ProcessInfo/',
        },
    'Base' :
        {
            'pyc' : base_path_ + 'Base/',
        }
    }


    #update environment path to include where components reside.
    sys.path.append(com_locations['CreateMD']['pyc'])
    sys.path.append(com_locations['AddFields']['pyc'])
    sys.path.append(com_locations['AddRasters']['pyc'])
    sys.path.append(com_locations['CreateRefMD']['pyc'])
    sys.path.append(com_locations['SetMDProperties']['pyc'])
    sys.path.append(com_locations['ProcessInfo']['pyc'])
    sys.path.append(com_locations['Base']['pyc'])


    #import all the modules required for the MDCS project.
    #import Base
    import CreateMD
    import AddFields
    import AddRasters
    import SetMDProperties
    import CreateRefMD
    import ProcessInfo


    def getProcessInfoValue(self, process, key, index = 0, indx = -1):
        if (index > len(self.processInfo.processInfo[process]) - 1):
            self.log('Error: Invalid command index.',
            self.const_critical_text)
            raise

        if (indx > -1):     # handle process info on keys [addindex, calculatevalues]
            if (key in self.processInfo.processInfo[process][index][indx].keys()):
                    return self.processInfo.processInfo[process][index][indx][key]
            return '#'

        if (key in self.processInfo.processInfo[process][index].keys()):
                return self.processInfo.processInfo[process][index][key]
        return '#'


    def run(self, conf, com, info):

        self.config = conf       #configuration/XML template
        self.userInfo = info     #callback information for commands /e.t.c.

        try:
            self.m_base.m_doc = minidom.parse(self.config)
            (ret, msg) = self.m_base.init()
            if (ret == False):
                if (msg == self.m_base.const_init_ret_version or
                    msg == self.m_base.const_init_ret_sde or
                    msg == self.m_base.const_init_ret_patch):
                    return False
                raise
        except Exception as inf:
            self.log("Error: reading input config file:" + self.config + "\n" + str(inf) + "\nQuitting...",
            self.const_critical_text)
            return False

        self.processInfo = self.ProcessInfo.ProcessInfo(self.m_base)
        bSuccess = self.processInfo.init(self.config)
        if (bSuccess == False):
            return False

        bSuccess = self.processInfo.hasProcessInfo

        #split commands with '+'
        self.log('Using template:' + self.config, self.const_general_text)

        com_ = com
        if (com_.upper() == self.const_cmd_default_text.upper()):
            try:
                com_ = self.getXMLNodeValue(self.m_base.m_doc, "Command")         #gets command defaults.
                self.log('Using default command(s):' + com_)

            except:
                self.log("Error: Reading input config file:" + self.config + "\nQuitting...",
                self.const_critical_text)
                return False

            if (len(com_.strip()) == 0):
                self.log('Error: Empty command.',
                self.const_critical_text)
                return False

        self.log('Processing command(s):' + com_.upper(), self.const_general_text)

        aryCmds = com_.split('+')
        for command in aryCmds:

            ucCommand = command
            command = command.upper()

            is_user_cmd = False

            cmd = ''.join(ch for ch in command if ch in (ascii_letters))
            index = 0
            if (len(command) > len(cmd)):
                    try:
                        index = int(command[len(cmd):])
                    except:
                        self.log("Command/Err: Invalid command index:" + command, self.const_warning_text)
                        # catch any float values entered, e.t.c

            if ((cmd in self.commands.keys()) == False):
                if (self.isUser_Function(ucCommand) == True):
                    try:
                        self.commands[ucCommand] = {}
                        self.commands[ucCommand]['desc'] = 'User defined command (%s)' % (ucCommand)
                        self.commands[ucCommand]['fnc'] = self.commands['CM']['fnc']        # can't use self.executeCommand directly here. Need to check.

                        cmd = ucCommand     # preseve user defined function case.
                        is_user_cmd = True
                    except:
                        self.log('Unabled to add user defined function/command (%s) to command chain.' % (ucCommand), self.const_warning_text)
                        return False    # return to prevent further processing.
                else:
                    self.log("Command/Err: Unknown command:" + cmd, self.const_general_text)
                    continue

            indexed_cmd = False if index == 0 else True
            cat_cmd  = '%s%s' % (cmd, '' if not indexed_cmd else index)
            if (self.isLog() == True):
                 self.m_log.CreateCategory(cat_cmd)

            self.log("Command:" + cat_cmd + '->' + '%s' % self.commands[cmd]['desc'], self.const_general_text)
            if (indexed_cmd):
                self.log('Using parameter values at index (%s)' % index, self.const_general_text)
            success = 'OK'

            status = self.commands[cmd]['fnc'](self, cmd, index)
            if (status == False):
                success = 'Failed!'
            self.log(success, self.const_status_text)

            if (self.isLog() == True):
                self.m_log.CloseCategory()

            if (status == False and     # do not continue with any following commands if AR / user defined function commands fail.
                (cmd == 'AR' or
                 is_user_cmd == True)):
                    return False

        return True
