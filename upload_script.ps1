# Base URL and endpoints
$baseUrl = "http://127.0.0.1:5000"
$formRenderUrl = "$baseUrl/teacher/dashboard"
$uploadUrl = "$baseUrl/teacher/teacher/upload_script"

# Create a session to keep cookies
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# 1. GET the dashboard page to extract CSRF token
$response = Invoke-WebRequest -Uri $formRenderUrl -WebSession $session
if ($response.Content -match 'name="csrf_token"\s+value="([^"]+)"') {
    $csrfToken = $matches[1]
    Write-Host "✅ Extracted CSRF Token: $csrfToken"
} else {
    Write-Error "❌ Could not find CSRF token!"
    exit
}

# 2. Prepare POST form data
$body = @{
    csrf_token = $csrfToken
    title = "PowerShell Upload Test"
    tags = "powershell,automated"
    answers_json = '[{"question": "Q1", "ideal_answer": "42"}]'
}

# 3. POST form data using the same session
$response = Invoke-WebRequest -Uri $uploadUrl -Method POST -Body $body -WebSession $session

# 4. Output response status and content
Write-Host "`n✅ Status Code: $($response.StatusCode)"
Write-Host "`n📄 Response Content:`n$response.Content"
