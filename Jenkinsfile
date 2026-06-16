import groovy.json.JsonOutput

pipeline {
    agent { label 'windows' }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    parameters {
        // ------------------------------------------------------------
        // Application / Release metadata
        // ------------------------------------------------------------
        string(name: 'APP_NAME', defaultValue: 'flask-release-demo', description: 'Application name')
        string(name: 'RELEASE_VERSION', defaultValue: '1.0.0', description: 'Release version / Git tag')
        string(name: 'EMAIL_SUBJECT_PREFIX', defaultValue: '[Release Automation]', description: 'Email subject prefix')

        // ------------------------------------------------------------
        // Email distribution
        // ------------------------------------------------------------
        string(name: 'EMAIL_TO', defaultValue: 'devopsuser8413@gmail.com', description: 'TO recipients (comma-separated)')
        string(name: 'EMAIL_CC', defaultValue: 'devopsuser8413@gmail.com', description: 'CC recipients (comma-separated)')
        string(name: 'EMAIL_BCC', defaultValue: 'devopsuser8413@gmail.com', description: 'BCC recipients (comma-separated)')
        string(name: 'EMAIL_FROM', defaultValue: 'projectworkuser@gmail.com', description: 'From address')
        string(name: 'EMAIL_REPLY_TO', defaultValue: 'projectworkuser@gmail.com', description: 'Reply-To address')

        booleanParam(name: 'PUBLISH_EMAIL', defaultValue: true, description: 'Send ZIPs by email')
        booleanParam(name: 'PUBLISH_CONFLUENCE', defaultValue: false, description: 'Publish ZIPs to Confluence')
        booleanParam(name: 'PUBLISH_GITHUB', defaultValue: false, description: 'Publish ZIPs to GitHub Release')

        // ------------------------------------------------------------
        // Optional uploaded deployment binary
        // ------------------------------------------------------------
        file(name: 'DEPLOYMENT_BINARY', description: 'Optional deployment binary/artifact. If omitted, Jenkins packages the Flask demo source.')

        // ------------------------------------------------------------
        // Multiple PDF release note upload slots
        // ------------------------------------------------------------
        file(name: 'RELEASE_NOTE_1', description: 'Release note PDF #1')
        file(name: 'RELEASE_NOTE_2', description: 'Release note PDF #2')
        file(name: 'RELEASE_NOTE_3', description: 'Release note PDF #3')
        file(name: 'RELEASE_NOTE_4', description: 'Release note PDF #4')
        file(name: 'RELEASE_NOTE_5', description: 'Release note PDF #5')
        file(name: 'RELEASE_NOTE_6', description: 'Release note PDF #6')
        file(name: 'RELEASE_NOTE_7', description: 'Release note PDF #7')
        file(name: 'RELEASE_NOTE_8', description: 'Release note PDF #8')

        // ------------------------------------------------------------
        // Confluence settings
        // ------------------------------------------------------------
        string(name: 'CONFLUENCE_BASE_URL', defaultValue: 'https://projectworkuser.atlassian.net/wiki', description: 'Confluence base URL')
        string(name: 'CONFLUENCE_SPACE_KEY', defaultValue: 'DEMO', description: 'Confluence space key')
        string(name: 'CONFLUENCE_PARENT_PAGE_ID', defaultValue: '131214', description: 'Optional Confluence parent page ID')

        // ------------------------------------------------------------
        // GitHub settings
        // ------------------------------------------------------------
        string(name: 'GITHUB_OWNER', defaultValue: 'pjwrkusr', description: 'GitHub owner / organisation')
        string(name: 'GITHUB_REPO', defaultValue: 'flask-demo-publish-docs', description: 'GitHub repository name')
    }

    environment {
        // ------------------------------------------------------------
        // Workspace / package paths
        // ------------------------------------------------------------
        RELEASE_NOTES_DIR = "release-notes"
        BUILD_INPUT_DIR   = "build-input"
        DIST_DIR          = "dist"

        RELEASE_NOTES_ZIP = "${params.APP_NAME}-${params.RELEASE_VERSION}-release-notes.zip"
        BINARIES_ZIP      = "${params.APP_NAME}-${params.RELEASE_VERSION}-deployment-binaries.zip"

        // ------------------------------------------------------------
        // Email environment variables
        // ------------------------------------------------------------
        EMAIL_TO_LIST   = "${params.EMAIL_TO}"
        EMAIL_CC_LIST   = "${params.EMAIL_CC}"
        EMAIL_BCC_LIST  = "${params.EMAIL_BCC}"
        EMAIL_FROM_ADDR = "${params.EMAIL_FROM}"
        EMAIL_REPLY_TO  = "${params.EMAIL_REPLY_TO}"
        EMAIL_SUBJECT   = "${params.EMAIL_SUBJECT_PREFIX} ${params.APP_NAME} ${params.RELEASE_VERSION}"

        // Optional SMTP credentials declaration
        // Credential type: Username with password
        SMTP_CREDS = credentials('smtp-projectwork-password')

        // ------------------------------------------------------------
        // Confluence environment variables
        // Credential type: Username with password
        // Credential ID: confluence-username-token
        // Creates:
        //   CONFLUENCE_CREDS_USR
        //   CONFLUENCE_CREDS_PSW
        // ------------------------------------------------------------
        CONFLUENCE_URL       = "${params.CONFLUENCE_BASE_URL}"
        CONFLUENCE_SPACE     = "${params.CONFLUENCE_SPACE_KEY}"
        CONFLUENCE_PARENT_ID = "${params.CONFLUENCE_PARENT_PAGE_ID}"
        CONFLUENCE_CREDS     = credentials('confluence-projectwork-token')

        // ------------------------------------------------------------
        // GitHub environment variables
        // Credential type: Secret text
        // Credential ID: github-token
        // ------------------------------------------------------------
        GH_OWNER = "${params.GITHUB_OWNER}"
        GH_REPO  = "${params.GITHUB_REPO}"
        GH_TOKEN = credentials('github-token')
    }

    stages {

        stage('Clean workspace') {
            steps {
                deleteDir()
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

                    Write-Host "Prepared workspace folders."
                '''
            }
        }

        stage('Collect and validate release note PDFs') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $uploadVars = @(
                        "RELEASE_NOTE_1",
                        "RELEASE_NOTE_2",
                        "RELEASE_NOTE_3",
                        "RELEASE_NOTE_4",
                        "RELEASE_NOTE_5",
                        "RELEASE_NOTE_6",
                        "RELEASE_NOTE_7",
                        "RELEASE_NOTE_8"
                    )

                    $pdfCount = 0

                    foreach ($varName in $uploadVars) {
                        $uploadedFile = [Environment]::GetEnvironmentVariable($varName)

                        if (-not [string]::IsNullOrWhiteSpace($uploadedFile)) {
                            if (Test-Path $uploadedFile) {
                                $extension = [System.IO.Path]::GetExtension($uploadedFile)
                                if ($extension -notin @(".pdf", ".PDF")) {
                                    throw "Uploaded file in $varName is not a PDF: $uploadedFile"
                                }

                                Copy-Item -Path $uploadedFile -Destination $env:RELEASE_NOTES_DIR -Force
                                $pdfCount++
                                Write-Host "Copied PDF: $uploadedFile"
                            }
                        }
                    }

                    if ($pdfCount -eq 0) {
                        throw "At least one release note PDF must be uploaded."
                    }

                    Write-Host "Validated and copied $pdfCount release note PDF(s) into $env:RELEASE_NOTES_DIR"
                '''
            }
        }

        stage('Collect deployment binary or package Flask demo') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $deploymentProvided = $false
                    $deploymentBinary = $env:DEPLOYMENT_BINARY

                    if (-not [string]::IsNullOrWhiteSpace($deploymentBinary) -and (Test-Path $deploymentBinary)) {
                        Copy-Item -Path $deploymentBinary -Destination $env:BUILD_INPUT_DIR -Force
                        $deploymentProvided = $true
                        Write-Host "Using uploaded deployment binary: $deploymentBinary"
                    }

                    if (-not $deploymentProvided) {
                        Write-Host "No deployment binary uploaded. Packaging Flask demo source."

                        # Create Python virtual environment (optional for demo validation)
                        python -m venv .venv
                        .\\.venv\\Scripts\\python.exe -m pip install --upgrade pip
                        .\\.venv\\Scripts\\pip.exe install -r requirements.txt

                        $appTarget = Join-Path $env:BUILD_INPUT_DIR $env:APP_NAME
                        New-Item -ItemType Directory -Force -Path $appTarget | Out-Null

                        Copy-Item -Path "app.py" -Destination $appTarget -Force
                        Copy-Item -Path "requirements.txt" -Destination $appTarget -Force

                        if (Test-Path "templates") {
                            Copy-Item -Path "templates" -Destination $appTarget -Recurse -Force
                        }

                        if (Test-Path "static") {
                            Copy-Item -Path "static" -Destination $appTarget -Recurse -Force
                        }

                        $runScript = @"
@echo off
python -m venv .venv
call .venv\\Scripts\\activate.bat
pip install -r requirements.txt
set APP_NAME=%APP_NAME%
set APP_VERSION=%RELEASE_VERSION%
python app.py
"@

                        Set-Content -Path (Join-Path $appTarget "run.bat") -Value $runScript -Encoding ASCII
                        Write-Host "Prepared demo Flask deployment package."
                    }
                '''
            }
        }

        stage('Create ZIP packages') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $releaseNotesZipPath = Join-Path $env:DIST_DIR $env:RELEASE_NOTES_ZIP
                    $binariesZipPath     = Join-Path $env:DIST_DIR $env:BINARIES_ZIP

                    if (Test-Path $releaseNotesZipPath) { Remove-Item $releaseNotesZipPath -Force }
                    if (Test-Path $binariesZipPath)     { Remove-Item $binariesZipPath -Force }

                    $pdfFiles = Get-ChildItem -Path $env:RELEASE_NOTES_DIR -Filter *.pdf -File -ErrorAction SilentlyContinue
                    if (-not $pdfFiles -or $pdfFiles.Count -eq 0) {
                        throw "No PDF files found in $env:RELEASE_NOTES_DIR"
                    }

                    Compress-Archive -Path "$env:RELEASE_NOTES_DIR\\*.pdf" -DestinationPath $releaseNotesZipPath -Force

                    $binaryItems = Get-ChildItem -Path $env:BUILD_INPUT_DIR
                    if (-not $binaryItems) {
                        throw "No deployment content found in $env:BUILD_INPUT_DIR"
                    }

                    Compress-Archive -Path "$env:BUILD_INPUT_DIR\\*" -DestinationPath $binariesZipPath -Force

                    Write-Host "Created ZIP packages:"
                    Get-ChildItem -Path $env:DIST_DIR | Format-Table Name, Length, LastWriteTime -AutoSize
                '''
            }
        }

        stage('Publish by Email') {
            when {
                expression { return params.PUBLISH_EMAIL }
            }
            steps {
                script {
                    // Merge TO + CC + BCC into one recipient list (compatible with all Jenkins versions)
                    def recipients = [
                        env.EMAIL_TO_LIST,
                        env.EMAIL_CC_LIST,
                        env.EMAIL_BCC_LIST
                    ]
                    .findAll { it?.trim() }
                    .join(',')

                    emailext(
                        subject: "${env.EMAIL_SUBJECT}",
                        to: recipients,
                        from: "${env.EMAIL_FROM_ADDR}",
                        replyTo: "${env.EMAIL_REPLY_TO}",
                        mimeType: 'text/html',
                        attachmentsPattern: "${env.DIST_DIR}/*.zip",
                        body: """
                            <p>Hello Team,</p>

                            <p>The release package for <strong>${params.APP_NAME}</strong>
                            version <strong>${params.RELEASE_VERSION}</strong> has been generated.</p>

                            <p><strong>Attached files</strong></p>
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

        stage('Publish to Confluence') {
            when {
                expression { return params.PUBLISH_CONFLUENCE }
            }
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    if ([string]::IsNullOrWhiteSpace($env:CONFLUENCE_URL)) {
                        throw "CONFLUENCE_BASE_URL is required when PUBLISH_CONFLUENCE is enabled."
                    }
                    if ([string]::IsNullOrWhiteSpace($env:CONFLUENCE_SPACE)) {
                        throw "CONFLUENCE_SPACE_KEY is required when PUBLISH_CONFLUENCE is enabled."
                    }

                    $pageTitle = "$env:APP_NAME $env:RELEASE_VERSION Release"
                    $pageBody  = @"
<h1>$env:APP_NAME $env:RELEASE_VERSION</h1>
<p>Automated release publication from Jenkins.</p>
<ul>
  <li>Release notes ZIP: $env:RELEASE_NOTES_ZIP</li>
  <li>Deployment binaries ZIP: $env:BINARIES_ZIP</li>
</ul>
"@

                    $payload = @{
                        type  = "page"
                        title = $pageTitle
                        space = @{
                            key = $env:CONFLUENCE_SPACE
                        }
                        body  = @{
                            storage = @{
                                value          = $pageBody
                                representation = "storage"
                            }
                        }
                    }

                    if (-not [string]::IsNullOrWhiteSpace($env:CONFLUENCE_PARENT_ID)) {
                        $payload["ancestors"] = @(
                            @{ id = $env:CONFLUENCE_PARENT_ID }
                        )
                    }

                    $jsonBody = $payload | ConvertTo-Json -Depth 20
                    $pair = "$env:CONFLUENCE_CREDS_USR`:$env:CONFLUENCE_CREDS_PSW"
                    $bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
                    $basicToken = [Convert]::ToBase64String($bytes)

                    $headers = @{
                        "Authorization" = "Basic $basicToken"
                        "Content-Type"  = "application/json"
                    }

                    $pageResponse = Invoke-RestMethod -Method Post `
                        -Uri "$env:CONFLUENCE_URL/rest/api/content/" `
                        -Headers $headers `
                        -Body $jsonBody

                    if (-not $pageResponse.id) {
                        throw "Confluence page creation failed. Page ID was not returned."
                    }

                    $pageId = "$($pageResponse.id)"
                    Write-Host "Created Confluence page ID: $pageId"

                    # Upload attachments using .NET multipart form-data
                    Add-Type -AssemblyName System.Net.Http

                    $attachmentHeaders = New-Object "System.Net.Http.Headers.AuthenticationHeaderValue"("Basic", $basicToken)

                    $filesToUpload = @(
                        (Join-Path $env:DIST_DIR $env:RELEASE_NOTES_ZIP),
                        (Join-Path $env:DIST_DIR $env:BINARIES_ZIP)
                    )

                    foreach ($filePath in $filesToUpload) {
                        if (-not (Test-Path $filePath)) {
                            throw "Attachment file not found: $filePath"
                        }

                        $client = New-Object System.Net.Http.HttpClient
                        $client.DefaultRequestHeaders.Authorization = $attachmentHeaders
                        $client.DefaultRequestHeaders.Add("X-Atlassian-Token", "no-check")

                        $multipart = New-Object System.Net.Http.MultipartFormDataContent
                        $fileBytes = [System.IO.File]::ReadAllBytes($filePath)
                        $fileContent = New-Object System.Net.Http.ByteArrayContent($fileBytes)
                        $fileContent.Headers.ContentType = [System.Net.Http.Headers.MediaTypeHeaderValue]::Parse("application/octet-stream")

                        $fileName = [System.IO.Path]::GetFileName($filePath)
                        $multipart.Add($fileContent, "file", $fileName)

                        $uploadResponse = $client.PostAsync("$env:CONFLUENCE_URL/rest/api/content/$pageId/child/attachment", $multipart).Result
                        if (-not $uploadResponse.IsSuccessStatusCode) {
                            $responseText = $uploadResponse.Content.ReadAsStringAsync().Result
                            throw "Failed to upload attachment to Confluence: $fileName. Status: $($uploadResponse.StatusCode). Response: $responseText"
                        }

                        Write-Host "Uploaded attachment to Confluence: $fileName"
                        $client.Dispose()
                    }
                '''
            }
        }

        stage('Publish to GitHub Release') {
            when {
                expression { return params.PUBLISH_GITHUB }
            }
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    if ([string]::IsNullOrWhiteSpace($env:GH_OWNER) -or [string]::IsNullOrWhiteSpace($env:GH_REPO)) {
                        throw "GITHUB_OWNER and GITHUB_REPO are required when PUBLISH_GITHUB is enabled."
                    }

                    $headers = @{
                        "Accept"               = "application/vnd.github+json"
                        "Authorization"        = "Bearer $env:GH_TOKEN"
                        "X-GitHub-Api-Version" = "2022-11-28"
                    }

                    $releasePayload = @{
                        tag_name   = $env:RELEASE_VERSION
                        name       = "$env:APP_NAME $env:RELEASE_VERSION"
                        body       = "Automated release for $env:APP_NAME $env:RELEASE_VERSION"
                        draft      = $false
                        prerelease = $false
                    } | ConvertTo-Json -Depth 10

                    $releaseApi = "https://api.github.com/repos/$env:GH_OWNER/$env:GH_REPO/releases"

                    $release = $null
                    try {
                        $release = Invoke-RestMethod -Method Post -Uri $releaseApi -Headers $headers -Body $releasePayload -ContentType "application/json"
                        Write-Host "Created new GitHub release."
                    }
                    catch {
                        Write-Host "GitHub release creation may have failed because the tag already exists. Attempting to fetch existing release by tag."
                        $release = Invoke-RestMethod -Method Get -Uri "https://api.github.com/repos/$env:GH_OWNER/$env:GH_REPO/releases/tags/$env:RELEASE_VERSION" -Headers $headers
                    }

                    if (-not $release.id -or -not $release.upload_url) {
                        throw "GitHub release ID or upload URL was not returned."
                    }

                    $releaseId = "$($release.id)"
                    $uploadUrl = "$($release.upload_url)" -replace "\\{\\?name,label\\}", ""

                    Write-Host "Using GitHub release ID: $releaseId"

                    # Get current assets
                    $assets = Invoke-RestMethod -Method Get -Uri "https://api.github.com/repos/$env:GH_OWNER/$env:GH_REPO/releases/$releaseId/assets" -Headers $headers

                    $targetAssetNames = @(
                        $env:RELEASE_NOTES_ZIP,
                        $env:BINARIES_ZIP
                    )

                    foreach ($asset in $assets) {
                        if ($targetAssetNames -contains $asset.name) {
                            Write-Host "Deleting existing GitHub asset: $($asset.name)"
                            Invoke-RestMethod -Method Delete -Uri "https://api.github.com/repos/$env:GH_OWNER/$env:GH_REPO/releases/assets/$($asset.id)" -Headers $headers
                        }
                    }

                    $filesToUpload = @(
                        (Join-Path $env:DIST_DIR $env:RELEASE_NOTES_ZIP),
                        (Join-Path $env:DIST_DIR $env:BINARIES_ZIP)
                    )

                    foreach ($filePath in $filesToUpload) {
                        if (-not (Test-Path $filePath)) {
                            throw "File not found for GitHub upload: $filePath"
                        }

                        $fileName = [System.IO.Path]::GetFileName($filePath)
                        $assetUploadUrl = "$uploadUrl?name=$fileName"

                        $uploadHeaders = @{
                            "Accept"               = "application/vnd.github+json"
                            "Authorization"        = "Bearer $env:GH_TOKEN"
                            "X-GitHub-Api-Version" = "2022-11-28"
                            "Content-Type"         = "application/zip"
                        }

                        Invoke-WebRequest -Method Post `
                            -Uri $assetUploadUrl `
                            -Headers $uploadHeaders `
                            -InFile $filePath `
                            -UseBasicParsing | Out-Null

                        Write-Host "Uploaded GitHub release asset: $fileName"
                    }
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'dist/*.zip', fingerprint: true, onlyIfSuccessful: false
            echo 'Pipeline finished.'
        }

        success {
            echo 'Success: release notes ZIP and deployment binaries ZIP were generated.'
        }

        failure {
            echo 'Failure: please review the stage logs above.'
        }
    }
}