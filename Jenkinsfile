@Library('main-shared-library') _
pipeline {

  agent {
    kubernetes {
      yaml kubernetes.base_pod([
        base_image_uri: "534369319675.dkr.ecr.us-west-2.amazonaws.com/sl-jenkins-base-ci:latest",
        ecr_uri: "534369319675.dkr.ecr.us-west-2.amazonaws.com",
        shell_memory_request: "300Mi",
        shell_cpu_request: "0.5",
        shell_memory_limit: "700Mi",
        shell_cpu_limit: "1",
        kaniko_memory_request: "1000Mi",
        kaniko_cpu_request: "2",
        kaniko_memory_limit: "1500Mi",
        kaniko_cpu_limit: "3",
        node_selector: "jenkins"
      ])
      defaultContainer 'shell'
    }
  }
  options {
    buildDiscarder logRotator(numToKeepStr: '30')
    timestamps()
  }
  parameters {
    choice(name: 'TEST_TYPE', choices: ['Tests parallel','Tests sequential','All Tests IN One Image'], description: 'Choose test type')
    string(name: 'LATEST', defaultValue: '', description: 'latest tag')
    string(name: 'APP_NAME', defaultValue: 'ahmad-BTQ', description: 'name of the app (integration build)')
    string(name: 'BRANCH', defaultValue: 'ahmad-branch', description: 'Branch to clone (ahmad-branch)')
    string(name: 'JOB_NAME', defaultValue: '', description: 'tests job name ')
    string(name: 'BUILD_BRANCH', defaultValue: 'ahmad-branch', description: 'Branch to Build images that have the creational LAB_ID (send to ahmad branch to build)')
    string(name: 'SL_TOKEN', defaultValue: '', description: 'sl-token')
    string(name: 'BUILD_NAME', defaultValue: '', description: 'build name')
    string(name: 'JAVA_AGENT_URL', defaultValue: 'https://storage.googleapis.com/cloud-profiler/java/latest/profiler_java_agent_alpine.tar.gz', description: 'use different java agent')
    string(name: 'DOTNET_AGENT_URL', defaultValue: 'https://agents.sealights.co/dotnetcore/latest/sealights-dotnet-agent-alpine-self-contained.tar.gz', description: 'use different dotnet agent')
    string(name: 'NODE_AGENT_URL', defaultValue: 'slnodejs', description: 'use different node agent')
    string(name: 'GO_AGENT_URL', defaultValue: 'https://agents.sealights.co/slgoagent/latest/slgoagent-linux-amd64.tar.gz', description: 'use different go agent')
    string(name: 'GO_SLCI_AGENT_URL', defaultValue: 'https://agents.sealights.co/slcli/latest/slcli-linux-amd64.tar.gz', description: 'use different slci go agent')
    string(name: 'PYTHON_AGENT_URL', defaultValue: 'sealights-python-agent', description: 'use different python agent')
    string(name: 'MACHINE', defaultValue: 'https://dev-integration.dev.sealights.co', description: 'machine env')

  }

  environment {
    DEV_INTEGRATION_SL_TOKEN = secrets.get_secret("mgmt/btq_token", "us-west-2")
    // DEV_INTEGRATION_LABID = "integ_master_BTQ"
  }

  stages {
    stage('Clone Repository') {
      steps {
        script {
          // Clone the repository with the specified branch
          git branch: params.BRANCH, url: 'https://github.com/Sealights/microservices-demo.git'
        }
      }
    }
    //Build parallel images
    stage ('Build BTQ') {
      steps {
        script {
          env.CURRENT_VERSION = "1-0-${BUILD_NUMBER}"
          def parallelLabs = [:]
          //List of all the images name
          env.TOKEN= "${params.SL_TOKEN}" == "" ? "${env.DEV_INTEGRATION_SL_TOKEN}"  : "${params.SL_TOKEN}"
          def services_list = ["adservice","cartservice","checkoutservice", "currencyservice","emailservice","frontend","paymentservice","productcatalogservice","recommendationservice","shippingservice"]
          //def special_services = ["cartservice"].
          env.BUILD_NAME= "${params.BUILD_NAME}" == "" ? "${params.BRANCH}-${env.CURRENT_VERSION}" : "${params.BUILD_NAME}"
          env.BUILD_NAME= "${params.BUILD_NAME}" == "" ? "${params.BRANCH}-${env.CURRENT_VERSION}" : "${params.BUILD_NAME}"
          services_list.each { service ->
            parallelLabs["${service}"] = {
              def AGENT_URL = getParamForService(service)
              build(job: 'BTQ-BUILD', parameters: [string(name: 'SERVICE', value: "${service}"),
                                                   string(name:'TAG' , value:"${env.CURRENT_VERSION}"),
                                                   string(name:'BRANCH' , value:"${params.BRANCH}"),
                                                   string(name:'BUILD_NAME' , value:"${env.BUILD_NAME}"),
                                                   string(name:'SL_TOKEN' , value:"${env.TOKEN}"),
                                                   string(name:'AGENT_URL' , value:AGENT_URL[0]),
                                                   string(name:'AGENT_URL_SLCI' , value:AGENT_URL[1])])
            }
          }
          parallel parallelLabs
        }
      }
    }

    stage ('Spin-Up BTQ') {
      steps {
        script{
          env.IDENTIFIER = "${params.BRANCH}-${env.CURRENT_VERSION}"
          env.MACHINE_DNS = "http://dev-${env.IDENTIFIER}.dev.sealights.co:8081"
          env.LAB_ID = sealights.create_lab_id(
            token: "${env.TOKEN}",
            machine: "${params.MACHINE}",
            app: "${params.APP_NAME}",
            branch: "${params.BUILD_BRANCH}",
            test_env: "${env.IDENTIFIER}",
            lab_alias: "${env.IDENTIFIER}",
            cdOnly: true,
          )

          build(job: 'SpinUpBoutiqeEnvironment', parameters: [
            string(name: 'ENV_TYPE', value: "DEV"),
            string(name:'IDENTIFIER' , value:"${env.IDENTIFIER}") ,
            string(name:'CUSTOM_EC2_INSTANCE_TYPE' , value:"t3a.large"),
            string(name:'GIT_BRANCH' , value:"${params.BRANCH}"),
            string(name:'BTQ_LAB_ID' , value:"${env.LAB_ID}"),
            string(name:'BTQ_TOKEN' , value:"${env.TOKEN}"),
            string(name:'BTQ_VERSION' , value:"${env.CURRENT_VERSION}"),
            string(name:'BUILD_NAME' , value:"${env.BUILD_NAME}"),
            string(name:'JAVA_AGENT_URL' , value: "${params.JAVA_AGENT_URL}"),
            string(name:'DOTNET_AGENT_URL' , value: "${params.DOTNET_AGENT_URL}")])
        }
      }
    }

    stage('All Tests IN One Image') {
      when {
        expression { params.TEST_TYPE == 'All Tests IN One Image' }
      }
      steps {
        script {
          sleep time: 150, unit: 'SECONDS'
          build(job: "All-In-Image", parameters: [
            string(name: 'BRANCH', value: "${params.BRANCH}"),
            string(name: 'SL_LABID', value: "${env.LAB_ID}"),
            string(name: 'SL_TOKEN', value: "${env.TOKEN}"),
            string(name: 'MACHINE_DNS', value: "${env.MACHINE_DNS}")
          ])

        }
      }
    }

    stage ('Run Tests parallel') {
      when {
        expression { params.TEST_TYPE == 'Tests parallel' }
      }
      steps {
        script {
          sleep time: 150, unit: 'SECONDS'
          //env.machine_dns = "http://dev-${env.IDENTIFIER}.dev.sealights.co:8081"
          def parallelLabs = [:]
          //List of all the jobs:
          def jobs_list = [
            "BTQ-java-tests(Junit without testNG)",
            "BTQ-python-tests(Pytest framework)",
            "BTQ-nodejs-tests(Mocha framework)",
            "BTQ-dotnet-tests(MS-test framework)",
            "BTQ-nodejs-tests(Jest framework)",
            "BTQ-python-tests(Robot framework)",
            "BTQ-dotnet-tests(NUnit-test framework)",
            "BTQ-java-tests(Junit support-testNG)",
            "BTQ-nodejs-tests-Cypress-framework",
            "BTQ-java-tests-SoapUi-framework",
            "BTQ-java-tests(Junit without testNG)-gradle",
            "BTQ-postman-tests",
            "BTQ-java-tests(Cucumber-framework-java)"

          ]

          jobs_list.each { job ->
            parallelLabs["${job}"] = {
              build(job:"${job}", parameters: [string(name: 'BRANCH', value: "${params.BRANCH}"),string(name: 'SL_LABID', value: "${env.LAB_ID}") , string(name:'SL_TOKEN' , value:"${env.TOKEN}") ,string(name:'MACHINE_DNS1' , value:"${env.MACHINE_DNS}")])
            }
          }
          parallel parallelLabs
        }
      }
    }




    stage('Run Tests sequential') {
      when {
        expression { params.TEST_TYPE == 'Tests sequential' }
      }
      steps {
        script {
          sleep time: 150, unit: 'SECONDS'
          // env.machine_dns = "http://dev-${env.IDENTIFIER}.dev.sealights.co:8081"
          def jobs_list = [
            "BTQ-java-tests(Junit without testNG)",
            "BTQ-python-tests(Pytest framework)",
            "BTQ-nodejs-tests(Mocha framework)",
            "BTQ-nodejs-tests(Jest framework)",
            "BTQ-python-tests(Robot framework)",
            "BTQ-java-tests(Junit support-testNG)",
            "BTQ-nodejs-tests-Cypress-framework",
            "BTQ-java-tests-SoapUi-framework",
            "BTQ-java-tests(Junit without testNG)-gradle",
            "BTQ-postman-tests",
            "BTQ-java-tests(Cucumber-framework-java)"

          ]

          jobs_list.each { job ->
            build(job: "${job}", parameters: [
              string(name: 'BRANCH', value: "${params.BRANCH}"),
              string(name: 'SL_LABID', value: "${env.LAB_ID}"),
              string(name: 'SL_TOKEN', value: "${env.TOKEN}"),
              string(name: 'MACHINE_DNS1', value: "${env.MACHINE_DNS}")
            ])
            sleep time: 60, unit: 'SECONDS'
          }
        }
      }
    }
  }



  post {
    success {
      script {
        build(job: 'TearDownBoutiqeEnvironment', parameters: [string(name: 'ENV_TYPE', value: "DEV"), string(name:'IDENTIFIER' , value:"${env.IDENTIFIER}")])
        slackSend channel: "#btq-ci", tokenCredentialId: "slack_sldevops", color: "good", message: "BTQ-CI build ${env.CURRENT_VERSION} for branch ${BRANCH_NAME} finished with status ${currentBuild.currentResult} (<${env.BUILD_URL}|Open> and TearDownBoutiqeEnvironment)"

        build(job: "changed", parameters: [

          string(name: 'APP_NAME', value: "${params.APP_NAME}"),
          string(name: 'BRANCH', value: "${params.BRANCH}"),
          string(name: 'JOB_NAME', value: "${params.JOB_NAME}"),
          string(name: 'BUILD_BRANCH', value: "${params.BUILD_BRANCH}"),
          string(name: 'SL_LABID', value: "${env.LAB_ID}"),
          string(name: 'SL_TOKEN', value: "${env.TOKEN}"),
          string(name: 'BUILD_NAME', value: "${params.BUILD_NAME}"),
          string(name: 'JAVA_AGENT_URL',value: "${params.JAVA_AGENT_URL}"),
          string(name: 'DOTNET_AGENT_URL', value: "${params.DOTNET_AGENT_URL}"),
          string(name: 'NODE_AGENT_URL', value: "${params.NODE_AGENT_URL}"),
          string(name: 'GO_AGENT_URL', value: "${params.GO_AGENT_URL}"),
          string(name: 'GO_SLCI_AGENT_URL', value: "${params.GO_SLCI_AGENT_URL}"),
          string(name: 'PYTHON_AGENT_URL', value: "${params.PYTHON_AGENT_URL}"),
          string(name: 'TEST_TYPE', value:'Tests parallel')
        ])

      }
    }
    failure {
      script {
        sts.set_assume_role([
          env: "dev",
          account_id: "159616352881",
          role_name: "CD-TF-Role"
        ])
        def env_instance_id = sh(returnStdout: true, script: "aws ec2 --region eu-west-1 describe-instances --filters 'Name=tag:Name,Values=EUW-ALLINONE-DEV-${env.IDENTIFIER}' 'Name=instance-state-name,Values=running' | jq -r '.Reservations[].Instances[].InstanceId'")
        sh "aws ec2 --region eu-west-1 stop-instances --instance-ids ${env_instance_id}"
        slackSend channel: "#btq-ci", tokenCredentialId: "slack_sldevops", color: "danger", message: "BTQ-CI build ${env.CURRENT_VERSION} for branch ${BRANCH_NAME} finished with status ${currentBuild.currentResult} (<${env.BUILD_URL}|Open>) and TearDownBoutiqeEnvironment"
      }
    }
  }
}

def getParamForService(service) {
  switch (service) {
    case "adservice":
      return [params.JAVA_AGENT_URL,""]
    case "cartservice":
      return [params.DOTNET_AGENT_URL,""]
    case ["checkoutservice","frontend","productcatalogservice","shippingservice"]:
      return [params.GO_AGENT_URL,params.GO_SLCI_AGENT_URL]
    case ["emailservice","recommendationservice"]:
      return [params.PYTHON_AGENT_URL,""]
    case ["currencyservice","paymentservice"]:
      return [params.NODE_AGENT_URL,""]

  }
}