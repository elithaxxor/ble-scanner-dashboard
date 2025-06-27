param(
    [int]$Interval = 5,
    [switch]$Continuous,
    [switch]$Threaded
)

Write-Host "`u{1F680} Launching scanner" -ForegroundColor Magenta
Write-Host "`u{1F50D} Starting BLE scan..." -ForegroundColor Cyan

do {
    $args = "--interval $Interval"
    if ($Threaded) { $args += " --threaded-scan" }
    python sniff_my_ble.py $args
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`u{1F389} `u{2705} Scan complete" -ForegroundColor Green
    } else {
        Write-Host "`u{274C} Scan error" -ForegroundColor Red
    }
    if (-not $Continuous) { break }
    Start-Sleep -Seconds $Interval
} while ($true)
