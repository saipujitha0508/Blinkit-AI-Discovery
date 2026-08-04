# Windows Task Scheduler Setup Script
# This script creates a weekly scheduled task for automated data updates

$ErrorActionPreference = "Stop"

# Get the project root directory
$ScriptPath = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $ScriptPath
$PythonScript = Join-Path $ProjectRoot "scripts\weekly_data_update.py"
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

# Task configuration
$TaskName = "Blinkit_Weekly_Data_Update"
$Description = "Automated weekly data scraping and analysis for Blinkit AI Discovery Engine"
$Schedule = "Weekly"  # Can be "Daily", "Weekly", "Monthly"
$DayOfWeek = 0  # 0 = Sunday, 1 = Monday, etc.
$StartTime = "02:00"  # 2 AM

Write-Host "Setting up Windows Task Scheduler for weekly data updates..." -ForegroundColor Green
Write-Host "Project Root: $ProjectRoot" -ForegroundColor Cyan
Write-Host "Python Script: $PythonScript" -ForegroundColor Cyan
Write-Host "Virtual Environment Python: $VenvPython" -ForegroundColor Cyan

# Check if files exist
if (-not (Test-Path $PythonScript)) {
    Write-Host "Error: Python script not found at $PythonScript" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $VenvPython)) {
    Write-Host "Error: Virtual environment Python not found at $VenvPython" -ForegroundColor Red
    exit 1
}

# Remove existing task if it exists
try {
    $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($ExistingTask) {
        Write-Host "Removing existing task '$TaskName'..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "Existing task removed." -ForegroundColor Green
    }
} catch {
    Write-Host "No existing task found, continuing..." -ForegroundColor Cyan
}

# Create the action
$Action = New-ScheduledTaskAction `
    -Execute $VenvPython `
    -Argument $PythonScript `
    -WorkingDirectory $ProjectRoot

# Create the trigger (weekly on Sunday at 2 AM)
$Trigger = New-ScheduledTaskTrigger `
    -Weekly `
    -DaysOfWeek $DayOfWeek `
    -At $StartTime

# Create the principal (run with highest privileges)
$Principal = New-ScheduledTaskPrincipal `
    -UserId "SYSTEM" `
    -LogonType ServiceAccount `
    -RunLevel Highest

# Create the settings
$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopOnIdleEnd `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5)

# Register the scheduled task
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Principal $Principal `
        -Settings $Settings `
        -Description $Description `
        -ErrorAction Stop
    
    Write-Host "✓ Scheduled task '$TaskName' created successfully!" -ForegroundColor Green
    Write-Host "  Schedule: Every Sunday at 2:00 AM" -ForegroundColor Cyan
    Write-Host "  Script: $PythonScript" -ForegroundColor Cyan
    Write-Host "  Working Directory: $ProjectRoot" -ForegroundColor Cyan
    
} catch {
    Write-Host "✗ Failed to create scheduled task: $_" -ForegroundColor Red
    exit 1
}

# Verify the task was created
try {
    $CreatedTask = Get-ScheduledTask -TaskName $TaskName
    Write-Host "✓ Task verification successful" -ForegroundColor Green
    Write-Host "  Next Run Time: $($CreatedTask.NextRunTime)" -ForegroundColor Cyan
    Write-Host "  Last Run Time: $($CreatedTask.LastRunTime)" -ForegroundColor Cyan
} catch {
    Write-Host "✗ Task verification failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "To manually run the task for testing:" -ForegroundColor Yellow
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Cyan
Write-Host ""
Write-Host "To view task history:" -ForegroundColor Yellow
Write-Host "  Get-ScheduledTaskInfo -TaskName '$TaskName'" -ForegroundColor Cyan
Write-Host ""
Write-Host "To delete the task:" -ForegroundColor Yellow
Write-Host "  Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false" -ForegroundColor Cyan
Write-Host ""
Write-Host "Setup completed successfully!" -ForegroundColor Green
