/***************************************************************************************************
 * JENKINS RELEASE AUTOMATION PIPELINE
 *
 * Purpose:
 *   - Process Release Notes PDF
 *   - Generate Release ZIP Packages
 *   - Send Release Email
 *   - Publish Release Assets to GitHub
 *   - Publish Release Information to Confluence
 *
 * Author  : Project Work User
 * Version : 1.0
 ***************************************************************************************************/

pipeline {

    /***********************************************************************************************
     * AGENT CONFIGURATION
     ***********************************************************************************************/
    agent any

    /***********************************************************************************************
     * PIPELINE OPTIONS
     ***********************************************************************************************/
    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        skipDefaultCheckout(true)
    }

    /***********************************************************************************************
     * BUILD PARAMETERS
     ***********************************************************************************************/
    parameters {

        // Application Information
        string(
            name: 'APP_NAME',
            defaultValue: 'flask-release-demo',
            description: 'Application name'
        )

        string(
            name: 'RELEASE_VERSION',
            defaultValue: '1.0.0',
            description: 'Release version'
        )

        // Email Configuration
        string(
            name: 'EMAIL_TO',
            defaultValue: 'projectworkuser@gmail.com',
            description: 'Primary recipients (comma-separated)'
        )

        string(
            name: 'EMAIL_CC',
            defaultValue: 'devopsuser8413@gmail.com',
            description: 'CC recipients (comma-separated)'
        )

        string(
            name: 'EMAIL_BCC',
            defaultValue: 'devopsuser8413@gmail.com',
            description: 'BCC recipients (comma-separated)'
        )

        string(
            name: 'EMAIL_FROM',
            defaultValue: 'projectworkuser@gmail.com',
            description: 'From address'
        )

        string(
            name: 'EMAIL_REPLY_TO',
            defaultValue: 'projectworkuser@gmail.com',
            description: 'Reply-To address'
        )

        // Publishing Options
        booleanParam(
            name: 'PUBLISH_EMAIL',
            defaultValue: true,
            description: 'Send email with ZIP attachments'
        )

        booleanParam(
            name: 'PUBLISH_TO_GITHUB',
            defaultValue: true,
            description: 'Create/update GitHub Release and upload ZIPs'
        )

        booleanParam(
            name: 'PUBLISH_TO_CONFLUENCE',
            defaultValue: true,
            description: 'Publish release information to Confluence'
        )

        // Release Notes
        // string(
        //     name: 'RELEASE_NOTE_PATH',
        //     defaultValue: 'C:\\Users\\I17270834\\Downloads\\Release_Notes_v1.0.0.pdf',
        //     description: 'Local PDF path on Jenkins server'
        // )

        stashedFile(
            name: 'RELEASE_NOTE_FILE',
            description: 'Upload Release Notes PDF'
        )

        // Confluence Configuration
        string(
            name: 'CONFLUENCE_BASE_URL',
            defaultValue: 'https://projectworkuser.atlassian.net/wiki',
            description: 'Confluence Base URL'
        )

        string(
            name: 'CONFLUENCE_SPACE_KEY',
            defaultValue: 'DEMO',
            description: 'Confluence Space Key'
        )

        string(
            name: 'CONFLUENCE_PARENT_PAGE_ID',
            defaultValue: '131214',
            description: 'Confluence Parent Page ID'
        )

        // GitHub Configuration
        string(
            name: 'GITHUB_OWNER',
            defaultValue: 'pjwrkusr',
            description: 'GitHub Organization/User'
        )

        string(
            name: 'GITHUB_REPO',
            defaultValue: 'flask-demo-publish-docs',
            description: 'GitHub Repository'
        )
    }

    /***********************************************************************************************
     * ENVIRONMENT VARIABLES
     ***********************************************************************************************/
    environment {

        // Working Directories
        RELEASE_NOTES_DIR = "release-notes"
        BUILD_INPUT_DIR   = "build-input"
        DIST_DIR          = "dist"

        // Output ZIP Files
        RELEASE_NOTES_ZIP = "${params.APP_NAME}-${params.RELEASE_VERSION}-release-notes.zip"
        BINARIES_ZIP      = "${params.APP_NAME}-${params.RELEASE_VERSION}-deployment-binaries.zip"

        // Email Settings
        EMAIL_TO_LIST   = "${params.EMAIL_TO}"
        EMAIL_CC_LIST   = "${params.EMAIL_CC}"
        EMAIL_BCC_LIST  = "${params.EMAIL_BCC}"
        EMAIL_FROM_ADDR = "${params.EMAIL_FROM}"
        EMAIL_REPLY_TO  = "${params.EMAIL_REPLY_TO}"

        // Confluence Settings
        CONFLUENCE_URL       = "${params.CONFLUENCE_BASE_URL}"
        CONFLUENCE_SPACE     = "${params.CONFLUENCE_SPACE_KEY}"
        CONFLUENCE_PARENT_ID = "${params.CONFLUENCE_PARENT_PAGE_ID}"

        // GitHub Settings
        GH_OWNER = "${params.GITHUB_OWNER}"
        GH_REPO  = "${params.GITHUB_REPO}"

        /*******************************************************************************************
         * CREDENTIALS
         *
         * confluence-projectwork-token
         *     Type: Username with Password
         *     Username: Atlassian Email
         *     Password: Atlassian API Token
         *
         * github-token-release
         *     Type: Secret Text
         *     Value: GitHub Personal Access Token
         *******************************************************************************************/
        CONFLUENCE_CREDS = credentials('confluence-projectwork-token')
        GH_TOKEN         = credentials('github-token-release')
    }

    /***********************************************************************************************
     * PIPELINE STAGES
     ***********************************************************************************************/
    stages {

        /*******************************************************************************************
         * STAGE 1 - CHECKOUT SOURCE CODE
         *******************************************************************************************/
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        /*******************************************************************************************
         * STAGE 2 - PREPARE WORKSPACE FOLDERS
         *******************************************************************************************/
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

        /*******************************************************************************************
         * STAGE 3 - PROCESS RELEASE NOTES PDF
         *******************************************************************************************/
        stage('Process release note') {
            steps {
                unstash 'RELEASE_NOTE_FILE'

                powershell '''
                    New-Item -ItemType Directory `
                        -Force `
                        -Path $env:RELEASE_NOTES_DIR | Out-Null

                    Copy-Item `
                        RELEASE_NOTE_FILE `
                        $env:RELEASE_NOTES_DIR `
                        -Force
                '''
            }
        }

        /*******************************************************************************************
         * STAGE 4 - CREATE RELEASE ZIP PACKAGES
         *
         * Generates:
         *   1. Release Notes ZIP
         *   2. Deployment Binaries ZIP
         *******************************************************************************************/
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

        /*******************************************************************************************
         * STAGE 5 - SEND RELEASE EMAIL
         *
         * Attachments:
         *   - Release Notes ZIP
         *   - Deployment Binaries ZIP
         *******************************************************************************************/
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

        /*******************************************************************************************
         * STAGE 6 - PUBLISH TO GITHUB
         *
         * Actions:
         *   - Create Release
         *   - Reuse Existing Release
         *   - Delete Existing Assets
         *   - Upload ZIP Files
         *******************************************************************************************/
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

        /*******************************************************************************************
         * STAGE 7 - PUBLISH TO CONFLUENCE
         *
         * Actions:
         *   - Retrieve Page Information
         *   - Increment Page Version
         *   - Update Page Content
         *   - Publish Release Details
         *******************************************************************************************/
        stage('Publish to Confluence') {
            when {
                expression { return params.PUBLISH_TO_CONFLUENCE }
            }

            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $pageId = "131214"

                    $pair = "$($env:CONFLUENCE_CREDS_USR):$($env:CONFLUENCE_CREDS_PSW)"
                    $base64 = [Convert]::ToBase64String(
                        [Text.Encoding]::ASCII.GetBytes($pair)
                    )

                    $headers = @{
                        Authorization = "Basic $base64"
                        Accept = "application/json"
                    }

                    Write-Host "Getting current page version..."

                    $searchUrl = "$env:CONFLUENCE_URL/rest/api/content?title=Flask&spaceKey=DEMO&expand=version"

                    $pageSearch = Invoke-RestMethod `
                        -Method Get `
                        -Uri $searchUrl `
                        -Headers $headers

                    if ($pageSearch.size -eq 0) {
                        throw "Confluence page not found."
                    }

                    $pageInfo = $pageSearch.results[0]

                    $pageId = $pageInfo.id
                    $currentVersion = $pageInfo.version.number
                    $newVersion = $currentVersion + 1

                    Write-Host "Page ID         : $pageId"
                    Write-Host "Current Version : $currentVersion"
                    Write-Host "New Version     : $newVersion"

                    $pageTitle = "$env:APP_NAME $env:RELEASE_VERSION Release"

                    $pageContent = @(
                        "<h1>$env:APP_NAME $env:RELEASE_VERSION Release</h1>",
                        "<p>Automated release publication from Jenkins.</p>",
                        "<p><strong>Release notes ZIP:</strong></p>",
                        "<p>$env:RELEASE_NOTES_ZIP</p>",
                        "<p><strong>Deployment binaries ZIP:</strong></p>",
                        "<p>$env:BINARIES_ZIP</p>"
                    ) -join ""

                    $payload = @{
                        id      = "$pageId"
                        type    = "page"
                        title   = $pageInfo.title
                        version = @{
                            number = $newVersion
                        }
                        body = @{
                            storage = @{
                                value = $pageContent
                                representation = "storage"
                            }
                        }
                    } | ConvertTo-Json -Depth 20

                    Write-Host "Updating Confluence page..."

                    $response = Invoke-RestMethod `
                        -Method Put `
                        -Uri "$env:CONFLUENCE_URL/rest/api/content/$pageId" `
                        -Headers @{
                            Authorization = "Basic $base64"
                            Accept = "application/json"
                            "Content-Type" = "application/json"
                        } `
                        -Body $payload

                    Write-Host "======================================"
                    Write-Host "Confluence page updated successfully."
                    Write-Host "Page ID : $($response.id)"
                    Write-Host "Version : $($response.version.number)"
                    Write-Host "======================================"
                '''
            }
        }
  }

    /***********************************************************************************************
     * POST BUILD ACTIONS
     ***********************************************************************************************/
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