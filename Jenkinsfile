pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        skipDefaultCheckout(true)
    }

    parameters {
        string(name: 'APP_NAME', defaultValue: 'flask-release-demo')
        string(name: 'RELEASE_VERSION', defaultValue: '1.0.0')

        string(name: 'EMAIL_TO', defaultValue: 'devopsuser8413@gmail.com')
        string(name: 'EMAIL_CC', defaultValue: '')
        string(name: 'EMAIL_BCC', defaultValue: '')
        string(name: 'EMAIL_FROM', defaultValue: 'projectworkuser@gmail.com')
        string(name: 'EMAIL_REPLY_TO', defaultValue: 'projectworkuser@gmail.com')

        booleanParam(name: 'PUBLISH_EMAIL', defaultValue: true)

        string(name: 'RELEASE_NOTE_PATH', defaultValue: 'C:\\Users\\I17270834\\Downloads\\Release_Notes_v1.0.0.pdf', description: 'Local file path on Jenkins machine')

        string(name: 'CONFLUENCE_BASE_URL', defaultValue: 'https://projectworkuser.atlassian.net/wiki')
        string(name: 'CONFLUENCE_SPACE_KEY', defaultValue: 'DEMO')
        string(name: 'CONFLUENCE_PARENT_PAGE_ID', defaultValue: '131214')

        string(name: 'GITHUB_OWNER', defaultValue: 'pjwrkusr')
        string(name: 'GITHUB_REPO', defaultValue: 'flask-demo-publish-docs')
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
            steps { checkout scm }
        }

        stage('Prepare folders') {
            steps {
                powershell '''
                    New-Item -ItemType Directory -Force -Path $env:RELEASE_NOTES_DIR | Out-Null
                    New-Item -ItemType Directory -Force -Path $env:BUILD_INPUT_DIR | Out-Null
                    New-Item -ItemType Directory -Force -Path $env:DIST_DIR | Out-Null
                '''
            }
        }

        stage('Process release note') {
            steps {
                powershell '''
                    $ErrorActionPreference = "Stop"

                    $file = "$env:RELEASE_NOTE_PATH"

                    if (-not (Test-Path $file)) {
                        throw "File not found: $file"
                    }

                    $ext = [System.IO.Path]::GetExtension($file)
                    if ($ext -ne ".pdf") {
                        throw "File must be PDF"
                    }

                    Copy-Item $file -Destination $env:RELEASE_NOTES_DIR -Force

                    Write-Host "Copied release note: $file"
                    Get-ChildItem $env:RELEASE_NOTES_DIR
                '''
            }
        }

        stage('Create ZIPs') {
            steps {
                powershell '''
                    $rn = Join-Path $env:DIST_DIR $env:RELEASE_NOTES_ZIP
                    $bin = Join-Path $env:DIST_DIR $env:BINARIES_ZIP

                    Compress-Archive "$env:RELEASE_NOTES_DIR\\*" $rn -Force

                    Copy-Item app.py $env:BUILD_INPUT_DIR -ErrorAction SilentlyContinue
                    Compress-Archive "$env:BUILD_INPUT_DIR\\*" $bin -Force
                '''
            }
        }

        stage('Send email') {
            when { expression { return params.PUBLISH_EMAIL } }
            steps {
                script {
                    def recipients = [
                        env.EMAIL_TO_LIST,
                        env.EMAIL_CC_LIST,
                        env.EMAIL_BCC_LIST
                    ].findAll { it?.trim() }.join(',')

                    emailext(
                        to: recipients,
                        subject: "Release ${params.RELEASE_VERSION}",
                        mimeType: 'text/html',
                        attachmentsPattern: "${env.DIST_DIR}/*.zip",
                        body: """
                        <p>Hello,</p>
                        <p>Release ${params.RELEASE_VERSION} generated.</p>
                        <p>Files attached.</p>
                        """
                    )
                }
            }
        }

        stage('Publish to GitHub') {
            when { expression { return false } } // disable for testing
            steps {
                powershell '''
                    Write-Host "GitHub step skipped for test"
                '''
            }
        }

        stage('Publish to Confluence') {
            when { expression { return false } }
            steps {
                powershell '''
                    Write-Host "Confluence step skipped for test"
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'dist/*.zip'
            echo "Done"
        }
    }
}