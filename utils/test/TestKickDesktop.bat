@ECHO OFF
rem ------------------------------------------------------------------------------
rem  Copyright 2015-2017 Esri
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
rem  TestKickDesktop.bat
rem ------------------------------------------------------------------------------
rem  requirements:
rem  * ArcGIS Desktop 10.X+
rem  * Python 2.7
rem  author: ArcGIS Solutions
rem  company: Esri
rem ==================================================
rem  description:
rem  This file starts the test running for Desktop (Python 2.7)
rem 
rem ==================================================
rem  history:
rem  10/06/2015 - MF - placeholder
rem  10/30/2015 - MF - tests running
rem  12/01/2015 - JH - added parameter for default log file name
rem  07/05/2016 - MF - updates to changes for Pro 1.3+
rem  02/24/2017 - MF - more updates for Pro 1.4.1/ArcMap 10.5
rem  07/20/2017 - MF - split BAT into PRO and MAP versions
rem ==================================================

REM === TEST SETUP ===================================
REM === TEST SETUP ===================================


REM === LOG SETUP ====================================
REM usage: set LOG=<defaultLogFileName.log>
REM name is optional; if not specified, name will be specified for you
set LOG=
REM === LOG SETUP ====================================

REM === RUN DESKTOP VERSION ==========================
REM If you have BOTH versions of Python installed use
REM these lines
REM ==================================================

ECHO Python 2.7 Tests ================================
REM The location of python.exe will depend upon your installation
REM of Python 2.7. Modify the following line as necessary:
"C:\Python27\ArcGIS10.5\python.exe" TestRunner.py %LOG%
REM check if Desktop for ArcGIS/Python 2.7 tests failed
IF %ERRORLEVEL% NEQ 0 (
   ECHO 'One or more tests failed'
) ELSE (
   ECHO 'Tests passed'
)
REM === RUN DESKTOP VERSION ==========================


REM === CLEANUP ======================================
REM === CLEANUP ======================================

EXIT /B %ERRORLEVEL%
