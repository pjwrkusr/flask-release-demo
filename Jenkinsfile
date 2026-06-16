pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        skipDefaultCheckout(true)
        timeout(time: 30, unit: 'MINUTES')
    }

    parameters {
        string(name: 'APP_NAME',         defaultValue: 'flask-release-demo', description: 'Application name')
        string(name: 'RELEASE_VERSION',  defaultValue: '1.0.0',              description: 'Release version (e.g. 1.0.0)')

        string(name: 'EMAIL_TO',         defaultValue: 'projectworkuser@gmail.com', description: 'Primary recipients (comma-separated)')
        string(name: 'EMAIL_CC',         defaultValue: '',                          description: 'CC recipients (comma-separated)')
        string(name: 'EMAIL_BCC',        defaultValue: '',                          description: 'BCC recipients (comma-separated)')
        string(name: 'EMAIL_FROM',       defaultValue: 'projectworkuser@gmail.com', description: 'From address')
        string(name: 'EMAIL_REPLY_TO',   defaultValue: 'projectworkuser@gmail.com', description: 'Reply-To address')

        booleanParam(name: 'PUBLISH_EMAIL',        defaultValue: true, description: 'Send email with ZIP attachments')
        booleanParam(name: 'PUBLISH_TO_GITHUB',    defaultValue: true, description: 'Create/update GitHub Release and upload ZIPs')
        booleanParam(name: 'PUBLISH_TO_CONFLUENCE', defaultValue: true, description: 'Create Confluence page and attach ZIPs')

        string(
            name: 'RELEASE_NOTE_PATH',
            defaultValue: 'C:\\Users\\I17270834\\Downloads\\Release_Notes_v1.0.0.pdf',
            description: 'Absolute path to the release note PDF on the Jenkins agent'
        )

        string(name: 'CONFLUENCE_BASE_URL',       defaultValue: 'https://projectworkuser.atlassian.net/wiki', description: 'Confluence base URL (no trailing slash)')
        string(name: 'CONFLUENCE_SPACE_KEY',      defaultValue: 'DEMO',   description: 'Confluence space key')
        string(name: 'CONFLUENCE_PARENT_PAGE_ID', defaultValue: '131214', description: 'Confluence parent page ID (leave blank to omit)')

        string(name: 'GITHUB_OWNER', defaultValue: 'pjwrkusr',                  description: 'GitHub owner / org')
        string(name: 'GITHUB_REPO',  defaultValue: 'flask-demo-publish-docs',   description: 'GitHub repository name')
    }

    environment {
        RELEASE_NOTES_DIR = 'release-notes'
        BUILD_INPUT_DIR   = 'build-input'
        DIST_DIR          = 'dist'

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

        // Credential bindings:
        //   confluence-projectwork-token  → Username with password  → CONFLUENCE_CREDS_USR / CONFLUENCE_CREDS_PSW
        //   github-token-release          → Secret text             → GH_TOKEN
        CONFLUENCE_CREDS = credentials('confluence-projectwork-token')
        GH_TOKEN         = credentials('github-token-release')
    }

    stages {

        // ─────────────────────────────────────────────────────────────────
        // 1. SOURCE CHECKOUT
        // ─────────────────────────────────────────────────────────────────
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        // ─────────────────────────────────────────────────────────────────
        // 2. PREPARE WORKSPACE FOLDERS
        // ─────────────────────────────────────────────────────────────────
        stage('Prepare folders') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    @($env:RELEASE_NOTES_DIR, $env:BUILD_INPUT_DIR, $env:DIST_DIR) | ForEach-Object {
                        New-Item -ItemType Directory -Force -Path $_ | Out-Null
                        Write-Host "Ensured directory: $_"
                    }
                '''
            }
        }

        // ─────────────────────────────────────────────────────────────────
        // 3. VALIDATE & COPY RELEASE NOTE PDF
        // ─────────────────────────────────────────────────────────────────
        stage('Process release note') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $file = $env:RELEASE_NOTE_PATH

                    if ([string]::IsNullOrWhiteSpace($file)) {
                        throw "RELEASE_NOTE_PATH parameter is empty."
                    }

                    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
                        throw "Release note file not found: $file"
                    }

                    $ext = [System.IO.Path]::GetExtension($file).ToLower()
                    if ($ext -ne ".pdf") {
                        throw "Release note must be a PDF file. Got: $ext"
                    }

                    Copy-Item -LiteralPath $file -Destination $env:RELEASE_NOTES_DIR -Force
                    Write-Host "Copied release note PDF to '$env:RELEASE_NOTES_DIR'."

                    Get-ChildItem $env:RELEASE_NOTES_DIR | Format-Table Name, Length, LastWriteTime -AutoSize
                '''
            }
        }

        // ─────────────────────────────────────────────────────────────────
        // 4. CREATE ZIP ARCHIVES
        // ─────────────────────────────────────────────────────────────────
        stage('Create ZIPs') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $rnZip  = Join-Path $env:DIST_DIR $env:RELEASE_NOTES_ZIP
                    $binZip = Join-Path $env:DIST_DIR $env:BINARIES_ZIP

                    # Remove stale ZIPs if present
                    @($rnZip, $binZip) | Where-Object { Test-Path $_ } | ForEach-Object {
                        Remove-Item $_ -Force
                        Write-Host "Removed stale ZIP: $_"
                    }

                    # --- Release notes ZIP ---
                    $rnFiles = Get-ChildItem -Path $env:RELEASE_NOTES_DIR -File -ErrorAction SilentlyContinue
                    if (-not $rnFiles) {
                        throw "No files found in '$env:RELEASE_NOTES_DIR'. Ensure the PDF was copied successfully."
                    }
                    Compress-Archive -Path (Join-Path $env:RELEASE_NOTES_DIR '*') -DestinationPath $rnZip -Force
                    Write-Host "Created release notes ZIP: $rnZip"

                    # --- Deployment binaries ZIP ---
                    if (Test-Path "app.py") {
                        Copy-Item "app.py" $env:BUILD_INPUT_DIR -Force
                    } else {
                        Write-Host "app.py not found — writing placeholder binary."
                        "Demo binary placeholder for $env:APP_NAME $env:RELEASE_VERSION" |
                            Out-File (Join-Path $env:BUILD_INPUT_DIR "placeholder.txt") -Encoding utf8
                    }
                    Compress-Archive -Path (Join-Path $env:BUILD_INPUT_DIR '*') -DestinationPath $binZip -Force
                    Write-Host "Created deployment binaries ZIP: $binZip"

                    Write-Host "`nDist folder contents:"
                    Get-ChildItem $env:DIST_DIR | Format-Table Name, Length, LastWriteTime -AutoSize
                '''
            }
        }

        // ─────────────────────────────────────────────────────────────────
        // 5. SEND EMAIL
        // ─────────────────────────────────────────────────────────────────
        stage('Send email') {
            when {
                expression { return params.PUBLISH_EMAIL }
            }
            steps {
                script {
                    // Build a clean recipient list; skip blank entries
                    def toList = env.EMAIL_TO_LIST?.trim()
                    if (!toList) {
                        error("EMAIL_TO is required when PUBLISH_EMAIL is enabled.")
                    }

                    def ccList  = env.EMAIL_CC_LIST?.trim()  ?: ''
                    def bccList = env.EMAIL_BCC_LIST?.trim() ?: ''

                    echo "Email  To : ${toList}"
                    echo "Email  CC : ${ccList ?: '(none)'}"
                    echo "Email BCC : ${bccList ?: '(none)'}"

                    emailext(
                        to:      toList,
                        cc:      ccList,
                        bcc:     bccList,
                        from:    env.EMAIL_FROM_ADDR,
                        replyTo: env.EMAIL_REPLY_TO,
                        subject: "[Release] ${params.APP_NAME} v${params.RELEASE_VERSION}",
                        mimeType: 'text/html',
                        attachmentsPattern: "${env.DIST_DIR}/*.zip",
                        body: """
                            <p>Hello,</p>
                            <p>Release <strong>${params.APP_NAME} v${params.RELEASE_VERSION}</strong>
                               has been generated and published.</p>
                            <p>The following ZIP files are attached to this email:</p>
                            <ul>
                                <li>${env.RELEASE_NOTES_ZIP}</li>
                                <li>${env.BINARIES_ZIP}</li>
                            </ul>
                            <p>Build: <a href="${env.BUILD_URL}">${env.JOB_NAME} #${env.BUILD_NUMBER}</a></p>
                            <p>Regards,<br/>Jenkins CI</p>
                        """
                    )

                    echo "Email sent successfully."
                }
            }
        }

        // ─────────────────────────────────────────────────────────────────
        // 6. PUBLISH TO GITHUB RELEASES
        // ─────────────────────────────────────────────────────────────────
        stage('Publish to GitHub') {
            when {
                expression { return params.PUBLISH_TO_GITHUB }
            }
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    # ── Input validation ──────────────────────────────────────────────
                    if ([string]::IsNullOrWhiteSpace($env:GH_OWNER)) { throw "GITHUB_OWNER is required." }
                    if ([string]::IsNullOrWhiteSpace($env:GH_REPO))  { throw "GITHUB_REPO is required."  }
                    if ([string]::IsNullOrWhiteSpace($env:GH_TOKEN)) { throw "GitHub token credential is missing." }

                    Write-Host "GitHub owner   : $env:GH_OWNER"
                    Write-Host "GitHub repo    : $env:GH_REPO"
                    Write-Host "Release tag    : $env:RELEASE_VERSION"

                    # ── Shared headers ────────────────────────────────────────────────
                    $headers = @{
                        "Accept"               = "application/vnd.github+json"
                        "Authorization"        = "Bearer $env:GH_TOKEN"
                        "X-GitHub-Api-Version" = "2022-11-28"
                    }

                    $baseApi    = "https://api.github.com/repos/$env:GH_OWNER/$env:GH_REPO"
                    $tagName    = $env:RELEASE_VERSION

                    # ── Helper: invoke with retry ─────────────────────────────────────
                    function Invoke-ApiWithRetry {
                        param(
                            [hashtable]$Params,
                            [int]$MaxAttempts = 3,
                            [int]$DelaySeconds = 5
                        )
                        for ($i = 1; $i -le $MaxAttempts; $i++) {
                            try {
                                return Invoke-RestMethod @Params
                            } catch {
                                if ($i -eq $MaxAttempts) { throw }
                                Write-Host "Attempt $i failed – retrying in ${DelaySeconds}s: $($_.Exception.Message)"
                                Start-Sleep -Seconds $DelaySeconds
                            }
                        }
                    }

                    # ── Create or fetch existing release ──────────────────────────────
                    $release = $null

                    $createParams = @{
                        Method      = "Post"
                        Uri         = "$baseApi/releases"
                        Headers     = $headers
                        ContentType = "application/json"
                        Body        = @{
                            tag_name   = $tagName
                            name       = "$env:APP_NAME $env:RELEASE_VERSION"
                            body       = "Automated release for $env:APP_NAME $env:RELEASE_VERSION via Jenkins build #$env:BUILD_NUMBER"
                            draft      = $false
                            prerelease = $false
                        } | ConvertTo-Json -Depth 10
                    }

                    try {
                        $release = Invoke-ApiWithRetry -Params $createParams
                        Write-Host "Created new GitHub release (id=$($release.id))."
                    } catch {
                        Write-Host "Create-release failed: $($_.Exception.Message)"
                        Write-Host "Attempting to fetch existing release by tag '$tagName'..."

                        $getParams = @{
                            Method  = "Get"
                            Uri     = "$baseApi/releases/tags/$tagName"
                            Headers = $headers
                        }
                        $release = Invoke-ApiWithRetry -Params $getParams
                        Write-Host "Fetched existing release (id=$($release.id))."
                    }

                    if (-not $release.id -or -not $release.upload_url) {
                        throw "GitHub release object is missing id or upload_url."
                    }

                    $releaseId = $release.id
                    # Strip URI template suffix {?name,label}
                    $uploadBase = $release.upload_url -replace '\{[^}]+\}', ''

                    Write-Host "Release ID   : $releaseId"
                    Write-Host "Upload base  : $uploadBase"

                    # ── Delete any pre-existing assets with the same name ─────────────
                    $existingAssets = Invoke-ApiWithRetry -Params @{
                        Method  = "Get"
                        Uri     = "$baseApi/releases/$releaseId/assets"
                        Headers = $headers
                    }

                    $targetNames = @($env:RELEASE_NOTES_ZIP, $env:BINARIES_ZIP)

                    foreach ($asset in $existingAssets) {
                        if ($targetNames -contains $asset.name) {
                            Write-Host "Deleting existing asset: $($asset.name) (id=$($asset.id))"
                            Invoke-ApiWithRetry -Params @{
                                Method  = "Delete"
                                Uri     = "$baseApi/releases/assets/$($asset.id)"
                                Headers = $headers
                            } | Out-Null
                        }
                    }

                    # ── Upload ZIP assets ─────────────────────────────────────────────
                    $filesToUpload = @(
                        (Join-Path $env:DIST_DIR $env:RELEASE_NOTES_ZIP),
                        (Join-Path $env:DIST_DIR $env:BINARIES_ZIP)
                    )

                    foreach ($filePath in $filesToUpload) {
                        if (-not (Test-Path -LiteralPath $filePath)) {
                            throw "Upload file not found: $filePath"
                        }

                        $fileName    = [System.IO.Path]::GetFileName($filePath)
                        $encodedName = [System.Uri]::EscapeDataString($fileName)
                        $assetUri    = "{0}?name={1}" -f $uploadBase, $encodedName

                        Write-Host "Uploading: $fileName → $assetUri"

                        Invoke-ApiWithRetry -Params @{
                            Method      = "Post"
                            Uri         = $assetUri
                            Headers     = $headers
                            InFile      = $filePath
                            ContentType = "application/zip"
                        } | Out-Null

                        Write-Host "Uploaded: $fileName"
                    }

                    Write-Host "✅ GitHub publish completed."
                '''
            }
        }

        // ─────────────────────────────────────────────────────────────────
        // 7. PUBLISH TO CONFLUENCE
        // ─────────────────────────────────────────────────────────────────
        stage('Publish to Confluence') {
            when {
                expression { return params.PUBLISH_TO_CONFLUENCE }
            }
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    # ── Input validation ──────────────────────────────────────────────
                    if ([string]::IsNullOrWhiteSpace($env:CONFLUENCE_URL))       { throw "CONFLUENCE_BASE_URL is required." }
                    if ([string]::IsNullOrWhiteSpace($env:CONFLUENCE_SPACE))     { throw "CONFLUENCE_SPACE_KEY is required." }
                    if ([string]::IsNullOrWhiteSpace($env:CONFLUENCE_CREDS_USR)) { throw "Confluence username credential is missing." }
                    if ([string]::IsNullOrWhiteSpace($env:CONFLUENCE_CREDS_PSW)) { throw "Confluence API token credential is missing." }

                    # Strip any trailing slash from the base URL
                    $baseUrl = $env:CONFLUENCE_URL.TrimEnd('/')

                    Write-Host "Confluence URL   : $baseUrl"
                    Write-Host "Space key        : $env:CONFLUENCE_SPACE"
                    Write-Host "Parent page ID   : $($env:CONFLUENCE_PARENT_ID -or '(none)')"

                    # ── Build page payload ────────────────────────────────────────────
                    $pageTitle = "$env:APP_NAME $env:RELEASE_VERSION Release"

                    $pageBody  = "<h1>$env:APP_NAME $env:RELEASE_VERSION</h1>"
                    $pageBody += "<p>Automated release published by Jenkins build "
                    $pageBody += "<a href='$env:BUILD_URL'>$env:JOB_NAME #$env:BUILD_NUMBER</a>.</p>"
                    $pageBody += "<h2>Attached Artifacts</h2><ul>"
                    $pageBody += "<li><strong>Release Notes ZIP:</strong> $env:RELEASE_NOTES_ZIP</li>"
                    $pageBody += "<li><strong>Deployment Binary ZIP:</strong> $env:BINARIES_ZIP</li>"
                    $pageBody += "</ul>"

                    $payload = [ordered]@{
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
                        $payload["ancestors"] = @( @{ id = $env:CONFLUENCE_PARENT_ID } )
                    }

                    $jsonBody = $payload | ConvertTo-Json -Depth 20
                    Set-Content -Path "page_payload.json" -Value $jsonBody -Encoding UTF8
                    Write-Host "Page payload written to page_payload.json."

                    # ── Create page ───────────────────────────────────────────────────
                    $createResponseFile = "confluence_create_response.json"

                    curl.exe -sS --fail-with-body `
                        -u "$env:CONFLUENCE_CREDS_USR`:$env:CONFLUENCE_CREDS_PSW" `
                        -H "Content-Type: application/json" `
                        -X POST `
                        --data @page_payload.json `
                        "$baseUrl/rest/api/content" `
                        -o $createResponseFile

                    if (-not (Test-Path $createResponseFile)) {
                        throw "No response received from Confluence create-page request."
                    }

                    $createResponseText = Get-Content $createResponseFile -Raw
                    Write-Host "Create-page response:"
                    Write-Host $createResponseText

                    $pageResponse = $createResponseText | ConvertFrom-Json -ErrorAction Stop

                    if (-not $pageResponse.id) {
                        # Surface the Confluence error message if available
                        $errMsg = $pageResponse.message ?? ($pageResponse | ConvertTo-Json -Depth 5)
                        throw "Confluence page creation failed: $errMsg"
                    }

                    $pageId = "$($pageResponse.id)"
                    Write-Host "✅ Created Confluence page (id=$pageId): $($pageResponse._links.base)$($pageResponse._links.webui)"

                    # ── Upload attachments ────────────────────────────────────────────
                    $filesToUpload = @(
                        (Join-Path $env:DIST_DIR $env:RELEASE_NOTES_ZIP),
                        (Join-Path $env:DIST_DIR $env:BINARIES_ZIP)
                    )

                    foreach ($filePath in $filesToUpload) {
                        if (-not (Test-Path -LiteralPath $filePath)) {
                            throw "Attachment not found: $filePath"
                        }

                        $fileName           = [System.IO.Path]::GetFileName($filePath)
                        $attachResponseFile = "attach_response_$fileName.json"

                        Write-Host "Uploading attachment: $fileName"

                        curl.exe -sS --fail-with-body `
                            -u "$env:CONFLUENCE_CREDS_USR`:$env:CONFLUENCE_CREDS_PSW" `
                            -H "X-Atlassian-Token: nocheck" `
                            -X POST `
                            -F "file=@$filePath;type=application/zip" `
                            "$baseUrl/rest/api/content/$pageId/child/attachment" `
                            -o $attachResponseFile

                        $attachResponseText = Get-Content $attachResponseFile -Raw
                        Write-Host "Attachment response for ${fileName}:"
                        Write-Host $attachResponseText

                        $attachResponse = $attachResponseText | ConvertFrom-Json -ErrorAction SilentlyContinue
                        if (-not $attachResponse.results -and -not $attachResponse.id) {
                            Write-Warning "Unexpected attachment response for $fileName — review the output above."
                        } else {
                            Write-Host "✅ Attached: $fileName"
                        }
                    }

                    Write-Host "✅ Confluence publish completed."
                '''
            }
        }
    }

    // ─────────────────────────────────────────────────────────────────────
    // POST ACTIONS
    // ─────────────────────────────────────────────────────────────────────
    post {
        always {
            archiveArtifacts artifacts: 'dist/*.zip', fingerprint: true, allowEmptyArchive: true
            // Clean up temporary JSON files created during the build
            powershell '''
                @("page_payload.json", "confluence_create_response.json") | ForEach-Object {
                    if (Test-Path $_) { Remove-Item $_ -Force; Write-Host "Cleaned up: $_" }
                }
                Get-ChildItem -Filter "attach_response_*.json" | Remove-Item -Force
            '''
        }
        success {
            echo "✅ Pipeline completed successfully — ${params.APP_NAME} v${params.RELEASE_VERSION}"
        }
        failure {
            echo "❌ Pipeline failed — check stage logs above for details."
        }
    }
}
