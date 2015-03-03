echo off
rem ------------------------------------------------------------------------------
rem  Copyright 2015 Esri
rem  Licensed under the Apache License, Version 2.0 (the "License");
rem  you may not use this file except in compliance with the License.
rem  You may obtain a copy of the License at
rem 
rem    http://www.apache.org/licenses/LICENSE-2.0
rem 
rem  Unless required by applicable law or agreed to in writing, software
rem  distributed under the License is distributed on an "AS IS" BASIS,
rem  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
rem  See the License for the specific language governing permissions and
rem  limitations under the License.
rem ------------------------------------------------------------------------------
rem  Name: config_mdcs.bat
rem  Description: Configure MDCS submodule
rem  Requirements:
rem ------------------------------------------------------------------------------
rem 3/5/2015 - mf - created BAT to automate file overlay to MDCS-PY
rem
rem ------------------------------------------------------------------------------

echo Initializing MDCS-PY submodule..
git submodule init
git submodule update

echo Copying Raster Function Templates...
copy *.rft.xml ..\mdcs\Parameter\RasterFunctionTemplates\*.*

echo Copying CIB Tools config files...
md ..\mdcs\Parameter\Config\CIB
copy S_CIB.XML ..\mdcs\Parameter\Config\CIB\S_CIB.XML

echo Copying Elevation Tools config files...
md ..\mdcs\Parameter\Config\Elevation
copy D_Mosaic.xml ..\mdcs\Parameter\Config\Elevation\D_Mosaic.xml
copy S_DTED.xml ..\mdcs\Parameter\Config\Elevation\S_DTED.xml
copy S_RasterData.xml ..\mdcs\Parameter\Config\Elevation\S_RasterData.xml

echo Copying CADRG ECRG Tools config files...
copy cadrgecrg.xml ..\mdcs\Parameter\Config\cadrgecrg.xml

echo Copying stats files...
copy SourceMD.xml ..\mdcs\Parameter\statistics\SourceMD.xml

echo Done!
