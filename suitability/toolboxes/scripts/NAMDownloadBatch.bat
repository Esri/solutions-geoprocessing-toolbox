ECHO off
rem -----------------------------------------------------------------------------
rem Copyright 2015 Esri
rem Licensed under the Apache License, Version 2.0 (the "License");
rem you may not use this file except in compliance with the License.
rem You may obtain a copy of the License at
rem 
rem   http://www.apache.org/licenses/LICENSE-2.0
rem 
rem Unless required by applicable law or agreed to in writing, software
rem distributed under the License is distributed on an "AS IS" BASIS,
rem WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
rem See the License for the specific language governing permissions and
rem limitations under the License.
rem -----------------------------------------------------------------------------
rem 
rem ==================================================
rem NAMDownloadBatch.bat
rem --------------------------------------------------
rem requirements:
rem * ArcGIS 10.3+
rem * Python 2.7
rem * Multidimension Supplemental Tools - download and install from:
rem     http://www.arcgis.com/home/item.html?id=9f963f362fe5417f87d44618796db938
rem author: ArcGIS Solutions
rem company: Esri
rem ==================================================
rem description:
rem Runs the NAMDownload.py 
rem 
rem ==================================================
rem history:
rem 9/21/2015 - AB - Original development
rem 12/3/2015 - MF - Updates for standards
rem ==================================================

ECHO on

REM Runs the Python update scripts needed

ECHO(>> %~dp0\DataDownload.txt
ECHO  -------------------------------------------------------------------------------------------------------------------------------->> %~dp0\DataDownload.txt
ECHO(>> %~dp0\DataDownload.txt
ECHO Started NAM data Transfer %Time% %Date%>> %~dp0\DataDownload.txt

python.exe .\NAMDownload.py

timeout /t 60

ECHO(>> %~dp0\DataDownload.txt
ECHO Finished NAM Data Transfer %Time% %Date% >> %~dp0\DataDownload.txt

REM PAUSE
