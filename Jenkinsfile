  properties(
      [
          pipelineTriggers([cron('TZ=US/Pacific\nH 7,16 * * *')]),
          parameters([choice(name: 'ENV', choices: ['staging', 'dev', 'demo', 'prod'], description: 'Select any of the env.'),
            
              [$class: 'CascadeChoiceParameter', 
                  choiceType: 'PT_SINGLE_SELECT',
                  description: 'Select a URL',
                  name: 'URL',
                  referencedParameters: 'ENV',
                  script: [$class: 'GroovyScript',
                      fallbackScript: [
                          classpath: [], 
                          sandbox: true, 
                          script: 'return ["https://stage-api2.augmedix.com/"]'
                      ],
                      script: [
                          classpath: [], 
                          sandbox: true, 
                          script: """
                              if (ENV == 'dev') { 
                                  return[
                                          'https://dev-api2.augmedix.com':'DEV-2 [https://dev-api2.augmedix.com]'
                                      ]
                              }
                              else if(ENV == 'demo'){
                                  return ['https://demo-api2.augmedix.com':'DEMO-2 [https://demo-api2.augmedix.com]']
                              }
                              else if(ENV == 'staging'){
                                  return ['https://staging-api2.augmedix.com':'STAGING-2 [https://staging-api2.augmedix.com]']
                              }else{
                                  return ['https://api2.augmedix.com':'PROD-2 [https://api2.augmedix.com]']
                              }
                          """.stripIndent()
                      ]
                  ]
              ],
            
              choice(name: 'TESTTYPE', choices: ['SANITY', 'REGRESSION', 'SECURITY', 'HEALTH_CHECK', 'NEGATIVE'], description: 'Select any of the testing types.'),

              [$class: 'CascadeChoiceParameter', 
                choiceType: 'PT_CHECKBOX',
                description: 'Select a choice',
                name: 'TESTCASE',
                script: [$class: 'GroovyScript',
                fallbackScript: [
                    classpath: [], 
                    sandbox: true, 
                    script: 'return ["ERROR"]'
                ],
                script: [
                    classpath: [], 
                    sandbox: true, 
                    script: """
                        return[
                               'testcases/test_authentication_service':'Authentication Service',
                               'testcases/test_ehr_appointments':'EHR Appointments',
                               'testcases/test_authorization_service':'Authorization Service',
                               'testcases/test_appointments':'Appointments',
                               'testcases/test_complaints':'Complaints',
                               'testcases/test_ehr_appointments_cache_false':'EHR Appointments Cache False',
                               'testcases/test_health_check':'Health Check',
                               'testcases/test_remote_state_graphql':'Remote State GraphQL',
                               'testcases/test_ehr_upload':'EHR Upload',
                               'testcases/test_app_sync':'App Sync',
                               'testcases/test_transcript':'Transcript'
                          ]
                        """.stripIndent()
                ]
            ]
        ]
              
          ])
      ]
  )
   
  node {
      try{
        def repoInformation = checkout scm
        def GIT_COMMIT_HASH = repoInformation.GIT_COMMIT

        def parallelTestConfiguration = [
          [
        
          '[Appointments]':'testcases/test_appointments',
          '[Audio Continuity]':'testcases/test_audio_continuity',
          '[Commure Templates]':'testcases/test_',
          '[Recording Process]':'testcases/test_recording_process',
          '[Remote State GraphQL]':'testcases/test_remote_state_graphql',
          '[Transcript]':'testcases/test_transcript'
          ]
        ]

        def stepList = prepareBuildStages(parallelTestConfiguration)

        for (def groupOfSteps in stepList) {
          parallel groupOfSteps
        }

        currentBuild.result = "SUCCESS"
      } catch(error) {
        currentBuild.result = "FAILURE"
        echo "The following error occurred: ${error}"
        throw error
      } finally {

        allure([
          includeProperties: false,
          jdk: '',
          properties: [],
  //         reportBuildPolicy: 'ALWAYS',
          results: [[path: 'target/allure-results']]
        ])
        
        
        stage("G-chat notifier"){
          def props = readProperties  file: 'resources/jenkins.properties'
    
          def gchat_webhook_link = props['gchat_webhook_link']
          wrap([$class: 'BuildUser']) {
              jobUserId = "${BUILD_USER_ID}"
              jobUserName = "${BUILD_USER}"
          }

          def now = new Date()

          if(jobUserId == "timer"){
            jobUserId = "SCHEDULER"
          }else{
            jobUserId = jobUserId.toUpperCase()
          }
          
            
          def summary = junit testResults: 'testResults/**/*.xml'
          def totalFailed = summary.failCount
          def totalCount = summary.totalCount
          double percentFailed = totalFailed * 100 / totalCount
          
          def summaryMsg = ""
          
          if(totalFailed){
              summaryMsg = "${summary.failCount} (${percentFailed.round(2)}%) failed out of ${summary.totalCount} test cases.\n\n"
          }else{
              summaryMsg = "All passed (out of ${totalCount})!!!\n\n"
          }

          def startMessage = "*AmbientAPIAutomation script execution is completed. Please see the details:*\n*------------------------------------------------------------------------------------------------------------------------------------------*\n\n"
          def buildStatus = "*Build status:* " + currentBuild.result + "\n"
          def buildNumber = "*Build number:* " + currentBuild.number + "\n"
          def buildInitiatedBy = "*Build Initiated by:* ${jobUserId}\n"
          def buildStarted = "*Build started:* " + env.BUILD_TIMESTAMP + "\n"
          def buildEnded = "*Build ended:* " + now.format("YYYY-MM-dd HH:mm:ss", TimeZone.getTimeZone('BST')) + " BDT\n"
          def buildDuration = "*Duration:* " + currentBuild.durationString + "\n\n"
          def testType = "*Test type:* ${TESTTYPE}\n"
          def testENV = "*Test ENV:* ${ENV}\n"
          def testURL = "*Test URL:* ${params.URL}\n"
          def buildURL = "*Build URL:* ${JOB_URL}\n"
          def reportLink = "*Report URL:* ${BUILD_URL}allure/\n\n"

          def message = startMessage + summaryMsg + buildStatus + buildNumber + buildInitiatedBy + buildStarted + buildEnded + buildDuration + testType + testENV + testURL + buildURL + reportLink


          googlechatnotification message: message, url:gchat_webhook_link
        }
      }
  }


  def prepareBuildStages(List<Map<String,String>> parallelTestConfiguration) {
    def stepList = []

    println('Preparing builds...')

    for (def parallelConfig in  parallelTestConfiguration) {
      def parallelSteps = prepareParallelSteps(parallelConfig)
      stepList.add(parallelSteps)
    }

    println(stepList)
    println('Finished preparing builds!')

    return stepList
  }


  def prepareParallelSteps(Map<String, String> parallelStepsConfig) {
    def testcases = params.TESTCASE
    String [] testcaseList = testcase.split(',')
    def parallelSteps = [:]
    
    if(testcases.getClass().isArray() ){
      for(def key in testcaseList){
        def tmp = key.split('/')
        def suiteName = tmp[tmp.size() - 1]
        parallelSteps.put(suiteName, prepareOneBuildStage(suiteName, key))
      }
    }else{
        for (def key in parallelStepsConfig.keySet()) {
        parallelSteps.put(key, prepareOneBuildStage(key, parallelStepsConfig[key]))
    }
    }

    return parallelSteps
  }


  def prepareOneBuildStage(String name, String file) {
    return {
      stage("Test: ${name}") {
          withCredentials([
              string(credentialsId: 'selenium_grid_16ram', variable: 'selenium_grid_16ram'),
              ]) { 
                sh """

                set +x
                . ~/.axgo_profile
                set -x
                rm -rf ${WORKSPACE}/allure-results && python3 -m pytest --env=${ENV.toLowerCase()} ${file}.py -m ${TESTTYPE.toLowerCase()} --junitxml=${WORKSPACE}/testResults/${file}.xml --enable-jenkins=yes --alluredir=${WORKSPACE}/allure-results -rA

                """
                
            }
      }
    }
  }
