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
        string(name: 'CONFLUENCE_PARENT_PAGE_ID', defaultValue: '131214', description: 'Confluence parent page ID')

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
        CONFLUENCE_CREDS     = credentials('confluence-projectwork-token')

        GH_OWNER = "${params.GITHUB_OWNER}"
        GH_REPO  = "${params.GITHUB_REPO}"
        GH_TOKEN = credentials('github-token')
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
                    echo "Email from      : ${env.EMAIL_FROM_ADDR}"
                    echo "Email reply-to  : ${env.EMAIL_REPLY_TO}"
                    echo "Attachments path: ${env.DIST_DIR}/*.zip"

                    try {
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
                        echo "emailext step executed."
                    } catch (Exception e) {
                        echo "Email sending failed: ${e.getMessage()}"
                        throw e
                    }
                }
            }
        }

        stage('Publish to GitHub') {
            when {
                expression { return false } // disabled for testing
            }
            steps {
                powershell '''
                    Write-Host "GitHub step skipped for test"
                '''
            }
        }

        stage('Publish to Confluence') {
            when {
                expression { return false } // disabled for testing
            }
            steps {
                powershell '''
                    Write-Host "Confluence step skipped for test"
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