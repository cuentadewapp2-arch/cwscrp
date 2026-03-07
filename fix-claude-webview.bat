@echo off
echo Closing Cursor cache fix - run this with Cursor CLOSED.
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0fix-claude-webview.ps1"
echo.
pause
