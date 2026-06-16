pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: '30'))
  }

  environment {
    email_from = 'jenkins.ci@senvion.in'
    TO_List    = 'Vedha.Rajeshwari.ext@senvion.in' 
    CC_List    = 'Vedha.Rajeshwari.ext@senvion.in'                                 
    BCC_List   = 'Vedha.Rajeshwari.ext@senvion.in'                                 

    DIST_DIR = 'dist'
    OUT_DIR  = 'out' 
  }

  parameters {
    choice(name: 'PLATFORM', choices: ['2xm', '3xm', '4xm'])
    string(name: 'BRANCH_NAME', defaultValue: 'Enter_Branch_Name_Here')

    choice(name: 'CONTROLLER', choices: [
        'src-MainController', 
        'src-HubController',
        'src-senvion_wtt_ctl-plc', 
        'src-SafetyController'
    ])

    booleanParam(name: 'MOD_HERK10', false)
    booleanParam(name: 'MOD_HERK01', false)
    booleanParam(name: 'MOD_GRIDMEAS', false)
    booleanParam(name: 'MOD_HCEBC10', false)
    booleanParam(name: 'MOD_HCEBC01', false)
    booleanParam(name: 'MOD_DYNCO05', false)

    choice(name: 'VERSION_TYPE', choices: ['alpha','beta','patch','minor','major','rc','custom'])
    string(name: 'CUSTOM_VERSION_STRING', defaultValue: '')

    booleanParam(name: 'SEND_EMAIL_NOTIFICATION', true)
    booleanParam(name: 'PUBLISH_TO_GITHUB_RELEASE', true)
    booleanParam(name: 'PUBLISH_TO_CONFLUENCE', true)

    string(name: 'CONFLUENCE_BASE_URL', defaultValue: 'https://senvionwind.atlassian.net/wiki')
    string(name: 'CONFLUENCE_SPACE_KEY', defaultValue: 'Jenkins')
    string(name: 'CONFLUENCE_PARENT_PAGE_ID', defaultValue: '')
  }

  stages {

    stage('Initialise Parameters') {
      steps {
        script {
          if (params.BRANCH_NAME == 'Enter_Branch_Name_Here') {
              error("Enter a valid branch name!")
          }

          if (params.PLATFORM == '2xm') {
            env.REPO_URL = 'https://github.com/ReTechnologies/TSW-RISE-0B.git'
          } else if (params.PLATFORM == '3xm') {
            env.REPO_URL = 'https://github.com/ReTechnologies/TSW-RISE-0B-3XM.git'
          } else if (params.PLATFORM == '4xm') {
            env.REPO_URL = 'https://github.com/ReTechnologies/TSW-RISE-0B-4XM.git'
          }

          def selectedFiles = []

          switch(params.CONTROLLER) {
            case 'src-MainController':
              if (params.MOD_HERK10) selectedFiles.add("HERK10.m")
              if (params.MOD_HERK01) selectedFiles.add("HERK01.m")
              if (params.MOD_GRIDMEAS) selectedFiles.add("GRIDMEAS.m")
              break

            case 'src-HubController':
              if (params.MOD_HCEBC10) selectedFiles.add("HCEBC10.m")
              if (params.MOD_HCEBC01) selectedFiles.add("HCEBC01.m")
              break

            case 'src-senvion_wtt_ctl-plc':
              if (params.MOD_DYNCO05) selectedFiles.add("DYNCO05.m")
              break

            case 'src-SafetyController':
              if (params.MOD_HERK10) selectedFiles.add("HERK10.m")
              break
          }

          env.TARGET_M_FILES = selectedFiles.join(", ")
          if (env.TARGET_M_FILES == "") {
            error("Select at least one module!")
          }
        }
      }
    }

    stage('Build and Copy (PowerShell script)') {
      steps {
        script {
          withCredentials([
            usernamePassword(credentialsId: 'github-credentials', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_PAT')
          ]) {
            powershell """
              \$ErrorActionPreference = 'Stop'

              \$repo = '${env.REPO_URL}'
              \$repo = \$repo -replace '^https://', ("https://{0}:{1}@" -f \$env:GIT_USER, \$env:GIT_PAT)

              Write-Host "Executing Build..."
              
              .\\build_and_copy.ps1 `
                -RemoteUrl "\$repo" `
                -BranchName "${params.BRANCH_NAME}" `
                -Controller "${params.CONTROLLER}" `
                -MFiles "${env.TARGET_M_FILES}"

              if (-not (Test-Path "${env.OUT_DIR}")) {
                throw "Output directory missing!"
              }
            """
          }
        }
      }
    }

    stage('Apply Deployment Versioning') {
      steps {
        script {

          writeFile file: 'versioning.ps1', text: '''
param ([string]$VersionType,[string]$CustomString)
$ErrorActionPreference="Stop"

if ($VersionType -eq "custom") {
 if ([string]::IsNullOrWhiteSpace($CustomString)) { throw "Custom version missing" }
 if (-not $CustomString.StartsWith("v")) { $CustomString="v"+$CustomString }
 Write-Output "##VERSION=$CustomString"
 exit 0
}

$base="1.0.0"
$count=1

switch ($VersionType) {
 "alpha" { $v="v$base-alpha.$count" }
 "beta"  { $v="v$base-beta.$count" }
 "rc"    { $v="v$base-rc.$count" }
 "patch" { $v="v1.0.$count" }
 "minor" { $v="v1.$count.0" }
 "major" { $v="v$count.0.0" }
}

Write-Output "##VERSION=$v"
'''

          def o = powershell(returnStdout: true,
            script: ".\\versioning.ps1 -VersionType '${params.VERSION_TYPE}' -CustomString '${params.CUSTOM_VERSION_STRING}'").trim()

          env.DEPLOY_VERSION = o.split('=')[1].trim()
          echo "Version: ${env.DEPLOY_VERSION}"
        }
      }
    }

    stage('Compress Build Output') {
      steps {
        script {
          env.ZIP_NAME="Build-${params.PLATFORM}-${env.DEPLOY_VERSION}.zip"
          env.ZIP_PATH="${env.WORKSPACE}\\${env.ZIP_NAME}"

          powershell """
            Compress-Archive -Path "${env.OUT_DIR}\\*" -DestinationPath "${env.ZIP_PATH}" -Force
          """
        }
      }
    }

    stage('Archive Artifacts') {
      steps {
        archiveArtifacts artifacts: "${env.ZIP_NAME}"
      }
    }

    stage('GitHub Release') {
      when { expression { params.PUBLISH_TO_GITHUB_RELEASE && currentBuild.currentResult=='SUCCESS' } }
      steps {
        script {
          withCredentials([
            usernamePassword(credentialsId: 'github-credentials', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_PAT')
          ]) {
            powershell """
              Write-Host "Creating GitHub Release..."
            """
          }
        }
      }
    }

    stage('Email Trigger') {
      when { expression { params.SEND_EMAIL_NOTIFICATION && currentBuild.currentResult=='SUCCESS' } }
      steps {
        emailext(
          subject: "Build Success ${env.DEPLOY_VERSION}",
          body: "Done",
          to: "${env.TO_List}",
          from: "${env.email_from}"
        )
      }
    }

    stage('Confluence Page') {
      when { expression { params.PUBLISH_TO_CONFLUENCE && currentBuild.currentResult=='SUCCESS' } }
      steps {
        script {
          echo "Publishing to Confluence..."
        }
      }
    }
  }

  post {
    success { echo "SUCCESS" }
    failure { echo "FAILURE" }
  }
}