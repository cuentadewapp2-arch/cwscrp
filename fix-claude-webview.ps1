# Fix "Error loading webview: Could not register service worker" for Claude window in Cursor
# Run this with Cursor CLOSED (File > Exit or close all Cursor windows).

$cursorRoaming = "$env:APPDATA\Cursor"
$foldersToClear = @(
    "Cache",
    "CachedData", 
    "Code Cache",
    "Service Worker",
    "GPUCache"
)

Write-Host "Cursor webview fix: clearing cache folders (Cursor must be closed)." -ForegroundColor Cyan
Write-Host ""

# Check if Cursor might still be running
$cursorProcesses = Get-Process -Name "Cursor" -ErrorAction SilentlyContinue
if ($cursorProcesses) {
    Write-Host "WARNING: Cursor appears to be running. Close Cursor completely first, then run this script again." -ForegroundColor Yellow
    Write-Host "  (File > Exit, or Task Manager > End task for all 'Cursor' processes)" -ForegroundColor Gray
    exit 1
}

foreach ($folder in $foldersToClear) {
    $path = Join-Path $cursorRoaming $folder
    if (Test-Path $path) {
        try {
            Remove-Item -Path $path -Recurse -Force -ErrorAction Stop
            Write-Host "  Cleared: $folder" -ForegroundColor Green
        } catch {
            Write-Host "  Failed to clear $folder : $_" -ForegroundColor Red
        }
    } else {
        Write-Host "  Skip (not found): $folder" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Done. You can open Cursor again and try the Claude window." -ForegroundColor Cyan
