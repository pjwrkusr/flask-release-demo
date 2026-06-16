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

        // Credentials:
        // - confluence-projectwork-token = Username with password
        // - github-token = Secret text
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
                    if ($ext -ne ".pdf" -and $ext -ne ".PDF") {
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
                        throw "GH_TOKEN is empty. Check Jenkins credential 'github-token'."
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
                        Write-Host "Create release failed. Trying to fetch existing release by tag..."
                        Write-Host $_.Exception.Message

                        $existingReleaseUrl = "https://api.github.com/repos/$env:GH_OWNER/$env:GH_REPO/releases/tags/$tagName"

                        $release = Invoke-RestMethod `
                            -Method Get `
                            -Uri $existingReleaseUrl `
                            -Headers $headers
                    }

                    if (-not $release.id -or -not $release.upload_url) {
                        throw "GitHub release ID or upload URL was not returned."
                    }

                    $releaseId = "$($release.id)"
                    $uploadUrl = "$($release.upload_url)" -replace "\\{\\?name,label\\}", ""

                    Write-Host "Using GitHub release ID: $releaseId"

                    # List current assets on the release
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
                            Invoke-RestMethod -Method Delete -Uri $deleteUrl -Headers $headers
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
                        $assetUploadUrl = "$uploadUrl?name=$fileName"

                        $uploadHeaders = @{
                            "Accept"               = "application/vnd.github+json"
                            "Authorization"        = "Bearer $env:GH_TOKEN"
                            "X-GitHub-Api-Version" = "2022-11-28"
                            "Content-Type"         = "application/zip"
                        }

                        Invoke-WebRequest `
                            -Method Post `
                            -Uri $assetUploadUrl `
                            -Headers $uploadHeaders `
                            -InFile $filePath `
                            -UseBasicParsing | Out-Null

                        Write-Host "Uploaded GitHub asset: $fileName"
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

                    if ([string]::IsNullOrWhiteSpace($env:CONFLUENCE_URL)) {
                        throw "CONFLUENCE_BASE_URL is required."
                    }

                    if ([string]::IsNullOrWhiteSpace($env:CONFLUENCE_SPACE)) {
                        throw "CONFLUENCE_SPACE_KEY is required."
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
                        -Uri "$env:CONFLUENCE_URL/rest/api/content" `
                        -Headers $headers `
                        -Body $jsonBody

                    if (-not $pageResponse.id) {
                        throw "Confluence page creation failed. Page ID not returned."
                    }

                    $pageId = "$($pageResponse.id)"
                    Write-Host "Created Confluence page ID: $pageId"

                    Add-Type -AssemblyName System.Net.Http
                    $attachmentHeaders = New-Object "System.Net.Http.Headers.AuthenticationHeaderValue"("Basic", $basicToken)

                    $filesToUpload = @(
                        (Join-Path $env:DIST_DIR $env:RELEASE_NOTES_ZIP),
                        (Join-Path $env:DIST_DIR $env:BINARIES_ZIP)
                    )

                    foreach ($filePath in $filesToUpload) {
                        if (-not (Test-Path $filePath)) {
                            throw "Confluence attachment file not found: $filePath"
                        }

                        $client = New-Object System.Net.Http.HttpClient
                        $client.DefaultRequestHeaders.Authorization = $attachmentHeaders
                        $client.DefaultRequestHeaders.Add("X-Atlassian-Token", "nocheck")

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

                        Write-Host "Uploaded Confluence attachment: $fileName"
                        $client.Dispose()
                    }
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