# Start a new PowerShell window to serve the templates folder, then open browser to user index
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$servePath = Join-Path $projectRoot "templates"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-Command","Set-Location -Path '$servePath'; python -m http.server 5501"
Start-Sleep -Seconds 1
Start-Process "http://127.0.0.1:5501/user/index.html"
