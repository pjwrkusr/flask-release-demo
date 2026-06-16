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

                    $owner = $env:GITHUB_ORG
                    $repo  = $env:GITHUB_REPO
                    $tag   = $env:RELEASE_VERSION

                    Write-Host "GitHub owner : $owner"
                    Write-Host "GitHub repo  : $repo"
                    Write-Host "Release tag  : $tag"

                    $headers = @{
                        Authorization = "Bearer $env:GH_TOKEN"
                        Accept = "application/vnd.github+json"
                        "X-GitHub-Api-Version" = "2022-11-28"
                        "User-Agent" = "Jenkins"
                    }

                    $release = $null

                    # --------------------------------------------------
                    # Create Release
                    # --------------------------------------------------
                    try {

                        $body = @{
                            tag_name = $tag
                            name = "$env:APP_NAME $tag"
                            generate_release_notes = $false
                            draft = $false
                            prerelease = $false
                        } | ConvertTo-Json

                        $release = Invoke-RestMethod `
                            -Method Post `
                            -Uri "https://api.github.com/repos/$owner/$repo/releases" `
                            -Headers $headers `
                            -Body $body `
                            -ContentType "application/json"

                        Write-Host "Release created successfully."

                    }
                    catch {

                        Write-Host "Create release failed."
                        Write-Host $_.Exception.Message

                        Write-Host "Fetching existing release by tag..."

                        $release = Invoke-RestMethod `
                            -Method Get `
                            -Uri "https://api.github.com/repos/$owner/$repo/releases/tags/$tag" `
                            -Headers $headers

                        Write-Host "Fetched existing release by tag."
                    }

                    $releaseId = $release.id

                    Write-Host "Using GitHub release ID: $releaseId"

                    # --------------------------------------------------
                    # Get Existing Assets
                    # --------------------------------------------------
                    $assets = Invoke-RestMethod `
                        -Method Get `
                        -Uri "https://api.github.com/repos/$owner/$repo/releases/$releaseId/assets" `
                        -Headers $headers

                    # --------------------------------------------------
                    # Upload Files
                    # --------------------------------------------------
                    $files = @(
                        (Join-Path $env:DIST_DIR $env:BINARIES_ZIP),
                        (Join-Path $env:DIST_DIR $env:RELEASE_NOTES_ZIP)
                    )

                    foreach ($filePath in $files) {

                        if (-not (Test-Path $filePath)) {
                            throw "File not found: $filePath"
                        }

                        $fileName = [System.IO.Path]::GetFileName($filePath)

                        # Delete existing asset if present
                        $existingAsset = $assets | Where-Object { $_.name -eq $fileName }

                        if ($existingAsset) {

                            Write-Host "Deleting existing asset: $fileName"

                            $deleteUrl = "https://api.github.com/repos/$owner/$repo/releases/assets/$($existingAsset.id)"

                            try {
                                Invoke-RestMethod `
                                    -Method Delete `
                                    -Uri $deleteUrl `
                                    -Headers $headers

                                Write-Host "Deleted existing asset successfully."
                            }
                            catch {
                                Write-Host "Failed to delete existing asset."
                                Write-Host $_.Exception.Message
                            }
                        }

                        Write-Host "Uploading: $fileName"

                        $uploadUrl = "https://uploads.github.com/repos/$owner/$repo/releases/$releaseId/assets?name=$fileName"

                        Invoke-RestMethod `
                            -Method Post `
                            -Uri $uploadUrl `
                            -Headers @{
                                Authorization = "Bearer $env:GH_TOKEN"
                                Accept = "application/vnd.github+json"
                                "Content-Type" = "application/zip"
                                "User-Agent" = "Jenkins"
                            } `
                            -InFile $filePath

                        Write-Host "Uploaded: $fileName"
                    }

                    Write-Host "======================================"
                    Write-Host "GitHub release publication completed."
                    Write-Host "======================================"
                '''
            }
        }
        stage('Test Confluence Connection') {
            when {
                expression { return params.PUBLISH_TO_CONFLUENCE }
            }

            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    Write-Host "Confluence URL: $env:CONFLUENCE_URL"

                    $pair = "$($env:CONFLUENCE_CREDS_USR):$($env:CONFLUENCE_CREDS_PSW)"
                    $base64 = [Convert]::ToBase64String(
                        [Text.Encoding]::ASCII.GetBytes($pair)
                    )

                    $headers = @{
                        Authorization = "Basic $base64"
                        Accept = "application/json"
                    }

                    try {
                        $result = Invoke-RestMethod `
                            -Method Get `
                            -Uri "$env:CONFLUENCE_URL/rest/api/space" `
                            -Headers $headers

                        Write-Host "SUCCESS - Confluence authentication works"
                        Write-Host "Spaces found: $($result.results.Count)"
                    }
                    catch {
                        Write-Host "FAILED"
                        Write-Host $_.Exception.Message

                        if ($_.Exception.Response) {
                            $reader = New-Object System.IO.StreamReader(
                                $_.Exception.Response.GetResponseStream()
                            )
                            $response = $reader.ReadToEnd()

                            Write-Host "Response:"
                            Write-Host $response
                        }

                        throw
                    }
                '''
            }
        }

        stage('Find Flask Page') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $pair = "$($env:CONFLUENCE_CREDS_USR):$($env:CONFLUENCE_CREDS_PSW)"
                    $base64 = [Convert]::ToBase64String(
                        [Text.Encoding]::ASCII.GetBytes($pair)
                    )

                    $headers = @{
                        Authorization = "Basic $base64"
                        Accept = "application/json"
                    }

                    $title = "Flask"

                    $url = "$env:CONFLUENCE_URL/rest/api/content?title=$title&spaceKey=DEMO&expand=version"

                    Write-Host "URL:"
                    Write-Host $url

                    $result = Invoke-RestMethod `
                        -Method Get `
                        -Uri $url `
                        -Headers $headers

                    $result | ConvertTo-Json -Depth 20
                '''
            }
        }
            // stage('Publish to Confluence') {
    //     when {
    //     expression { return params.PUBLISH_TO_CONFLUENCE }
    //     }

    // steps {
    //     powershell '''
    //         $ErrorActionPreference = "Stop"

    //         # --------------------------------------------------
    //         # Validation
    //         # --------------------------------------------------
    //         if ([string]::IsNullOrWhiteSpace($env:CONFLUENCE_URL)) {
    //             throw "CONFLUENCE_BASE_URL is required."
    //         }

    //         if ([string]::IsNullOrWhiteSpace($env:CONFLUENCE_CREDS_USR) -or
    //             [string]::IsNullOrWhiteSpace($env:CONFLUENCE_CREDS_PSW)) {
    //             throw "Confluence credentials are missing."
    //         }

    //         $pageId = $env:CONFLUENCE_PARENT_ID

    //         if ([string]::IsNullOrWhiteSpace($pageId)) {
    //             throw "CONFLUENCE_PARENT_PAGE_ID is required."
    //         }

    //         Write-Host "======================================"
    //         Write-Host "Confluence Configuration"
    //         Write-Host "======================================"
    //         Write-Host "URL      : $env:CONFLUENCE_URL"
    //         Write-Host "Page ID  : $pageId"
    //         Write-Host "User     : $env:CONFLUENCE_CREDS_USR"
    //         Write-Host "======================================"

    //         # --------------------------------------------------
    //         # Authentication
    //         # --------------------------------------------------
    //         $authBytes = [System.Text.Encoding]::ASCII.GetBytes(
    //             "$($env:CONFLUENCE_CREDS_USR):$($env:CONFLUENCE_CREDS_PSW)"
    //         )

    //         $authToken = [Convert]::ToBase64String($authBytes)

    //         $headers = @{
    //             Authorization = "Basic $authToken"
    //             Accept        = "application/json"
    //         }

    //         # --------------------------------------------------
    //         # Get Current Page Information
    //         # --------------------------------------------------
    //         $pageInfoUrl = "$env:CONFLUENCE_URL/rest/api/content/$pageId?expand=version"

    //         Write-Host "Fetching current page information..."

    //         $pageInfo = Invoke-RestMethod `
    //             -Method Get `
    //             -Uri $pageInfoUrl `
    //             -Headers $headers

    //         $newVersion = $pageInfo.version.number + 1

    //         Write-Host "Current Version : $($pageInfo.version.number)"
    //         Write-Host "New Version     : $newVersion"

    //         # --------------------------------------------------
    //         # Build Page Content
    //         # --------------------------------------------------
    //         $pageTitle = "$env:APP_NAME $env:RELEASE_VERSION Release"

    //         $pageContent = @(
    //             "<h1>$env:APP_NAME $env:RELEASE_VERSION Release</h1>",
    //             "<p>Automated release publication from Jenkins.</p>",
    //             "<p><strong>Release notes ZIP:</strong></p>",
    //             "<p>$env:RELEASE_NOTES_ZIP</p>",
    //             "<p><strong>Deployment binaries ZIP:</strong></p>",
    //             "<p>$env:BINARIES_ZIP</p>",
    //             "<hr/>",
    //             "<p><strong>Application:</strong> $env:APP_NAME</p>",
    //             "<p><strong>Version:</strong> $env:RELEASE_VERSION</p>",
    //             "<p><strong>Published By:</strong> Jenkins Pipeline</p>",
    //             "<p><strong>Status:</strong> Successful</p>"
    //         ) -join ""

    //         # --------------------------------------------------
    //         # Update Existing Page
    //         # --------------------------------------------------
    //         $payload = @{
    //             id      = "$pageId"
    //             type    = "page"
    //             title   = $pageTitle

    //             version = @{
    //                 number = $newVersion
    //             }

    //             body = @{
    //                 storage = @{
    //                     value          = $pageContent
    //                     representation = "storage"
    //                 }
    //             }
    //         } | ConvertTo-Json -Depth 20

    //         Write-Host "Updating Confluence page..."

    //         Invoke-RestMethod `
    //             -Method Put `
    //             -Uri "$env:CONFLUENCE_URL/rest/api/content/$pageId" `
    //             -Headers @{
    //                 Authorization = "Basic $authToken"
    //                 Accept        = "application/json"
    //                 "Content-Type" = "application/json"
    //             } `
    //             -Body $payload

    //         Write-Host "======================================"
    //         Write-Host "Confluence page updated successfully."
    //         Write-Host "======================================"
    //     '''
    //   }
    // }

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