ECHO off

REM Runs the Python update scripts needed
ECHO(>> %~dp0\DataDownload.txt
ECHO Started NAM data Transfer %Time% %Date%>> %~dp0\DataDownload.txt


CALL python C:\MAOW\Scripts\NAMDownload.py
IF %ERRORLEVEL% NEQ 0 (
   ECHO 'NAMDownload script had errors'
)


timeout /t 60
ECHO(>> %~dp0\DataDownload.txt
ECHO Finished NAM Data Transfer %Time% %Date% >> %~dp0\DataDownload.txt

REM PAUSE

