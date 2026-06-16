pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        skipDefaultCheckout(true)
    }

    parameters {
        string(name: 'APP_NAME', defaultValue: 'flask-release-demo', description: 'Application name')
        string(name: 'RELEASE_VERSION', defaultValue: '1.0.0', description: 'Release version')

        string(name: 'EMAIL_TO', defaultValue: 'projectworkuser@gmail.com', description: 'Primary recipients (comma-separated)')
        string(name: 'EMAIL_CC', defaultValue: '', description: 'CC recipients (comma-separated)')
        string(name: 'EMAIL_BCC', defaultValue: '', description: 'BCC recipients (comma-separated)')
        string(name: 'EMAIL_FROM', defaultValue: 'projectworkuser@gmail.com', description: 'From address')
        string(name: 'EMAIL_REPLY_TO', defaultValue: 'projectworkuser@gmail.com', description: 'Reply-To address')

        booleanParam(name: 'PUBLISH_EMAIL', defaultValue: true, description: 'Send email with ZIP attachments')
        booleanParam(name: 'PUBLISH_TO_GITHUB', defaultValue: true, description: 'Create/update GitHub Release and upload ZIPs')
        booleanParam(name: 'PUBLISH_TO_CONFLUENCE', defaultValue: true, description: 'Create Confluence page and attach ZIPs')

        string(
            name: 'RELEASE_NOTE_PATH',
            defaultValue: 'C:\\Users\\I17270834\\Downloads\\Release_Notes_v1.0.0.pdf',
            description: 'Local file path on Jenkins machine'
        )

        string(
            name: 'CONFLUENCE_BASE_URL',
            defaultValue: 'https://projectworkuser.atlassian.net/wiki',
            description: 'Confluence base URL'
        )
        string(name: 'CONFLUENCE_SPACE_KEY', defaultValue: 'DEMO', description: 'Confluence space key')
        string(name: 'CONFLUENCE_PARENT_PAGE_ID', defaultValue: '131214', description: 'Confluence parent page ID (optional)')

        string(name: 'GITHUB_OWNER', defaultValue: 'pjwrkusr', description: 'GitHub owner')
        string(name: 'GITHUB_REPO', defaultValue: 'flask-demo-publish-docs', description: 'GitHub repository')
    }

    environment {
        RELEASE_NOTES_DIR = "release-notes"
        BUILD_INPUT_DIR   = "build-input"
        DIST_DIR          = "dist"

        RELEASE_NOTES_ZIP = "${params.APP_NAME}-${params.RELEASE_VERSION}-release-notes.zip"
        BINARIES_ZIP      = "${params.APP_NAME}-${params.RELEASE_VERSION}-deployment-binaries.zip"

        EMAIL_TO_LIST   = "${params.EMAIL_TO}"
        EMAIL_CC_LIST   = "${params.EMAIL_CC}"
        EMAIL_BCC_LIST  = "${params.EMAIL_BCC}"
        EMAIL_FROM_ADDR = "${params.EMAIL_FROM}"
        EMAIL_REPLY_TO  = "${params.EMAIL_REPLY_TO}"

        CONFLUENCE_URL       = "${params.CONFLUENCE_BASE_URL}"
        CONFLUENCE_SPACE     = "${params.CONFLUENCE_SPACE_KEY}"
        CONFLUENCE_PARENT_ID = "${params.CONFLUENCE_PARENT_PAGE_ID}"

        GH_OWNER = "${params.GITHUB_OWNER}"
        GH_REPO  = "${params.GITHUB_REPO}"

        // Credentials
        // confluence-projectwork-token = Username with password (email + API token)
        // github-token-release         = Secret text
        CONFLUENCE_CREDS = credentials('confluence-projectwork-token')
        GH_TOKEN         = credentials('github-token-release')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Prepare folders') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    New-Item -ItemType Directory -Force -Path $env:RELEASE_NOTES_DIR | Out-Null
                    New-Item -ItemType Directory -Force -Path $env:BUILD_INPUT_DIR   | Out-Null
                    New-Item -ItemType Directory -Force -Path $env:DIST_DIR          | Out-Null

                    Write-Host "Prepared folders:"
                    Write-Host " - $env:RELEASE_NOTES_DIR"
                    Write-Host " - $env:BUILD_INPUT_DIR"
                    Write-Host " - $env:DIST_DIR"
                '''
            }
        }

        stage('Process release note') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $file = "$env:RELEASE_NOTE_PATH"

                    if ([string]::IsNullOrWhiteSpace($file)) {
                        throw "RELEASE_NOTE_PATH is empty."
                    }

                    if (-not (Test-Path $file)) {
                        throw "File not found: $file"
                    }

                    $ext = [System.IO.Path]::GetExtension($file)
                    if ($ext -notin @(".pdf", ".PDF")) {
                        throw "File must be PDF: $file"
                    }

                    Copy-Item $file -Destination $env:RELEASE_NOTES_DIR -Force

                    Write-Host "Copied release note: $file"
                    Get-ChildItem $env:RELEASE_NOTES_DIR | Format-Table Name, Length, LastWriteTime -AutoSize
                '''
            }
        }

        stage('Create ZIPs') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $rn  = Join-Path $env:DIST_DIR $env:RELEASE_NOTES_ZIP
                    $bin = Join-Path $env:DIST_DIR $env:BINARIES_ZIP

                    if (Test-Path $rn)  { Remove-Item $rn -Force }
                    if (Test-Path $bin) { Remove-Item $bin -Force }

                    $releaseItems = Get-ChildItem -Path $env:RELEASE_NOTES_DIR -File -ErrorAction SilentlyContinue
                    if (-not $releaseItems) {
                        throw "No files found in release notes directory."
                    }

                    Compress-Archive -Path "$env:RELEASE_NOTES_DIR\\*" -DestinationPath $rn -Force

                    if (Test-Path "app.py") {
                        Copy-Item app.py $env:BUILD_INPUT_DIR -Force
                    } else {
                        "Demo binary placeholder" | Out-File (Join-Path $env:BUILD_INPUT_DIR "placeholder.txt") -Encoding utf8
                    }

                    Compress-Archive -Path "$env:BUILD_INPUT_DIR\\*" -DestinationPath $bin -Force

                    Write-Host "Created ZIPs:"
                    Get-ChildItem $env:DIST_DIR | Format-Table Name, Length, LastWriteTime -AutoSize
                '''
            }
        }

        stage('Send email') {
            when {
                expression { return params.PUBLISH_EMAIL }
            }
            steps {
                script {
                    def recipients = [
                        env.EMAIL_TO_LIST,
                        env.EMAIL_CC_LIST,
                        env.EMAIL_BCC_LIST
                    ].findAll { it?.trim() }.join(',')

                    echo "Email recipients: ${recipients}"
                    echo "Attachments path: ${env.DIST_DIR}/*.zip"

                    emailext(
                        to: recipients,
                        from: "${env.EMAIL_FROM_ADDR}",
                        replyTo: "${env.EMAIL_REPLY_TO}",
                        subject: "Release ${params.RELEASE_VERSION}",
                        mimeType: 'text/html',
                        attachmentsPattern: "${env.DIST_DIR}/*.zip",
                        body: """
                            <p>Hello,</p>
                            <p>Release <strong>${params.RELEASE_VERSION}</strong> has been generated.</p>
                            <p>The following ZIP files are attached:</p>
                            <ul>
                                <li>${env.RELEASE_NOTES_ZIP}</li>
                                <li>${env.BINARIES_ZIP}</li>
                            </ul>
                            <p>Regards,<br/>Jenkins</p>
                        """
                    )
                }
            }
        }

        stage('Publish to GitHub') {
            when {
                expression { return params.PUBLISH_TO_GITHUB }
            }
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    if ([string]::IsNullOrWhiteSpace($env:GH_OWNER) -or [string]::IsNullOrWhiteSpace($env:GH_REPO)) {
                        throw "GITHUB_OWNER and GITHUB_REPO are required."
                    }

                    if ([string]::IsNullOrWhiteSpace($env:GH_TOKEN)) {
                        throw "GH_TOKEN is empty."
                    }

                    Write-Host "GitHub owner : $env:GH_OWNER"
                    Write-Host "GitHub repo  : $env:GH_REPO"
                    Write-Host "Release tag  : $env:RELEASE_VERSION"

                    $headers = @{
                        "Accept"               = "application/vnd.github+json"
                        "Authorization"        = "Bearer $env:GH_TOKEN"
                        "X-GitHub-Api-Version" = "2022-11-28"
                    }

                    $tagName    = "$env:RELEASE_VERSION"
                    $releaseApi = "https://api.github.com/repos/$env:GH_OWNER/$env:GH_REPO/releases"

                    $releasePayload = @{
                        tag_name   = $tagName
                        name       = "$env:APP_NAME $env:RELEASE_VERSION"
                        body       = "Automated release for $env:APP_NAME $env:RELEASE_VERSION"
                        draft      = $false
                        prerelease = $false
                    } | ConvertTo-Json -Depth 10

                    $release = $null
                    $createFailed = $false

                    try {
                        $release = Invoke-RestMethod `
                            -Method Post `
                            -Uri $releaseApi `
                            -Headers $headers `
                            -Body $releasePayload `
                            -ContentType "application/json"

                        Write-Host "Created new GitHub release."
                    }
                    catch {
                        $createFailed = $true
                        Write-Host "Create release failed."
                        Write-Host $_.Exception.Message
                    }

                    if (-not $release) {
                        try {
                            $existingReleaseUrl = "https://api.github.com/repos/$env:GH_OWNER/$env:GH_REPO/releases/tags/$tagName"
                            $release = Invoke-RestMethod `
                                -Method Get `
                                -Uri $existingReleaseUrl `
                                -Headers $headers

                            Write-Host "Fetched existing release by tag."
                        }
                        catch {
                            Write-Host "Lookup existing release by tag failed."
                            Write-Host $_.Exception.Message

                            if ($createFailed) {
                                throw "GitHub create-release failed, and no existing release was found by tag '$tagName'."
                            } else {
                                throw
                            }
                        }
                    }

                    if (-not $release.id -or -not $release.upload_url) {
                        throw "GitHub release ID or upload URL was not returned."
                    }

                    $releaseId = "$($release.id)"
                    $uploadUrl = "$($release.upload_url)" -replace "\\{\\?name,label\\}", ""

                    Write-Host "Using GitHub release ID: $releaseId"
                    Write-Host "Resolved upload URL base: $uploadUrl"

                    $assetsUrl = "https://api.github.com/repos/$env:GH_OWNER/$env:GH_REPO/releases/$releaseId/assets"
                    $assets = Invoke-RestMethod -Method Get -Uri $assetsUrl -Headers $headers

                    $targetAssetNames = @(
                        $env:RELEASE_NOTES_ZIP,
                        $env:BINARIES_ZIP
                    )

                    foreach ($asset in $assets) {
                        if ($targetAssetNames -contains $asset.name) {
                            Write-Host "Deleting existing asset: $($asset.name)"
                            $deleteUrl = "https://api.github.com/repos/$env:GH_OWNER/$env:GH_REPO/releases/assets/$($asset.id)"
                            Invoke-RestMethod -Method Delete -Uri $deleteUrl -Headers $headers | Out-Null
                        }
                    }

                    $filesToUpload = @(
                        (Join-Path $env:DIST_DIR $env:RELEASE_NOTES_ZIP),
                        (Join-Path $env:DIST_DIR $env:BINARIES_ZIP)
                    )

                    foreach ($filePath in $filesToUpload) {
                        if (-not (Test-Path $filePath)) {
                            throw "GitHub upload file not found: $filePath"
                        }

                        $fileName = [System.IO.Path]::GetFileName($filePath)
                        $encodedName = [System.Uri]::EscapeDataString($fileName)
                        $assetUploadUrl = "{0}?name={1}" -f $uploadUrl, $encodedName

                        Write-Host "Uploading asset: $fileName"
                        Write-Host "Upload URL: $assetUploadUrl"

                        $uploadResponse = Invoke-RestMethod `
                            -Method Post `
                            -Uri $assetUploadUrl `
                            -Headers $headers `
                            -InFile $filePath `
                            -ContentType "application/zip"

                        Write-Host "Uploaded GitHub asset: $fileName"
                        if ($uploadResponse.browser_download_url) {
                            Write-Host "Download URL: $($uploadResponse.browser_download_url)"
                        }
                    }
                '''
            }
        }

        stage('Publish to Confluence') {
            when {
                expression { return params.PUBLISH_TO_CONFLUENCE }
            }
            steps {
                powershell '''
$ErrorActionPreference = "Stop"

# Validate required values
if ([string]::IsNullOrWhiteSpace($env:CONFLUENCE_URL)) {
    throw "CONFLUENCE_BASE_URL is required."
}

if ([string]::IsNullOrWhiteSpace($env:CONFLUENCE_SPACE)) {
    throw "CONFLUENCE_SPACE_KEY is required."
}

if ([string]::IsNullOrWhiteSpace($env:CONFLUENCE_CREDS_USR) -or
    [string]::IsNullOrWhiteSpace($env:CONFLUENCE_CREDS_PSW)) {
    throw "Confluence credentials are missing."
}

# Make the page title unique to avoid common duplicate-title conflicts
$pageTitle = "$env:APP_NAME $env:RELEASE_VERSION Build $env:BUILD_NUMBER"

$pageBody = "<h1>$env:APP_NAME $env:RELEASE_VERSION</h1>" +
            "<p>Automated release from Jenkins.</p>" +
            "<ul>" +
            "<li><b>Release Notes ZIP:</b> $env:RELEASE_NOTES_ZIP</li>" +
            "<li><b>Deployment Binary ZIP:</b> $env:BINARIES_ZIP</li>" +
            "</ul>"

$payload = @{
    type  = "page"
    title = $pageTitle
    space = @{ key = $env:CONFLUENCE_SPACE }
    body  = @{
        storage = @{
            value          = $pageBody
            representation = "storage"
        }
    }
}

if (-not [string]::IsNullOrWhiteSpace($env:CONFLUENCE_PARENT_ID)) {
    $payload["ancestors"] = @(@{ id = $env:CONFLUENCE_PARENT_ID })
}

$jsonBody = $payload | ConvertTo-Json -Depth 20
Set-Content -Path page_payload.json -Value $jsonBody -Encoding UTF8

Write-Host "Creating Confluence page: $pageTitle"
Write-Host "Confluence URL: $env:CONFLUENCE_URL"
Write-Host "Space key: $env:CONFLUENCE_SPACE"

$responseFile = "confluence_create_response.json"
$statusCode = curl.exe -sS `
  -u "$env:CONFLUENCE_CREDS_USR`:$env:CONFLUENCE_CREDS_PSW" `
  -H "Content-Type: application/json" `
  -X POST `
  --data-binary "@page_payload.json" `
  "$env:CONFLUENCE_URL/rest/api/content" `
  -o $responseFile `
  -w "%{http_code}"

if (-not (Test-Path $responseFile)) {
    throw "No response file returned from Confluence create page request."
}

$responseText = Get-Content $responseFile -Raw
Write-Host "Confluence create-page HTTP status: $statusCode"
Write-Host "Create page response:"
Write-Host $responseText

if ($statusCode -notin @("200","201")) {
    throw "Confluence page creation failed with HTTP status $statusCode. Review the response above."
}

$pageResponse = $responseText | ConvertFrom-Json

if (-not $pageResponse.id) {
    throw "Confluence page creation succeeded technically, but page ID was not returned."
}

$pageId = "$($pageResponse.id)"
Write-Host "Created Confluence page ID: $pageId"

$filesToUpload = @(
    (Join-Path $env:DIST_DIR $env:RELEASE_NOTES_ZIP),
    (Join-Path $env:DIST_DIR $env:BINARIES_ZIP)
)

foreach ($filePath in $filesToUpload) {
    if (-not (Test-Path $filePath)) {
        throw "Attachment file not found: $filePath"
    }

    $fileName = [System.IO.Path]::GetFileName($filePath)
    Write-Host "Uploading attachment: $fileName"

    $safeName = $fileName -replace '[^a-zA-Z0-9._-]', '_'
    $attachResponseFile = "attach_${safeName}.json"

    $attachStatus = curl.exe -sS `
      -u "$env:CONFLUENCE_CREDS_USR`:$env:CONFLUENCE_CREDS_PSW" `
      -H "X-Atlassian-Token: nocheck" `
      -X POST `
      -F "file=@$filePath" `
      "$env:CONFLUENCE_URL/rest/api/content/$pageId/child/attachment" `
      -o $attachResponseFile `
      -w "%{http_code}"

    $attachResponseText = ""
    if (Test-Path $attachResponseFile) {
        $attachResponseText = Get-Content $attachResponseFile -Raw
    }

    Write-Host "Attachment upload status for $fileName: $attachStatus"
    Write-Host "Attachment upload response for $fileName:"
    Write-Host $attachResponseText

    if ($attachStatus -notin @("200","201")) {
        throw "Attachment upload failed for $fileName with HTTP status $attachStatus"
    }
}

Write-Host "Confluence publish completed successfully"
'''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'dist/*.zip', fingerprint: true, onlyIfSuccessful: false
            echo "Done"
        }
        success {
            echo "Pipeline completed successfully."
        }
        failure {
            echo "Pipeline failed."
        }
    }
}