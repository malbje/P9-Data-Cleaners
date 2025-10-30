<#
PowerShell helper: Log in using the first customer email found in the local DB
and fetch that user's appointments from the running Flask server.

Usage (from project root):
    .\scripts\fetch_appointments_for_first_user.ps1

Notes:
- Requires the Flask dev server to be running at http://127.0.0.1:5000
- Uses the Python helper scripts/get_first_user_email.py to read the DB locally.
#>

$base = 'http://127.0.0.1:5000'

Write-Host "Looking up a customer email from local DB..."

$py = "python" # Adjust if your environment needs `python3`
$email = & $py "scripts/get_first_user_email.py" 2>&1 | Out-String
$email = $email.Trim()

if (-not $email) {
    Write-Host "No customer email found in DB or error running helper." -ForegroundColor Red
    exit 1
}

Write-Host "Using email: $email"

# Create a web session to preserve cookies
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# Log in (development login accepts email only)
$loginBody = @{ email = $email; password = 'ignored' } | ConvertTo-Json
try {
    $loginResp = Invoke-RestMethod -Uri "$base/api/auth/login" -Method Post -Body $loginBody -ContentType 'application/json' -WebSession $session
    Write-Host "Login response:`n" ($loginResp | ConvertTo-Json -Depth 4)
} catch {
    Write-Host "Login failed: $_" -ForegroundColor Red
    exit 2
}

# Fetch appointments for the logged-in session
try {
    $appts = Invoke-RestMethod -Uri "$base/api/appointments" -Method Get -WebSession $session -ContentType 'application/json'
    Write-Host "Appointments:`n" ($appts | ConvertTo-Json -Depth 6)
} catch {
    Write-Host "Failed to fetch appointments: $_" -ForegroundColor Red
    exit 3
}
