pipeline {
    agent any

    environment {
        AUTH_TOKEN = '' // Initialize the token variable
    }

    stages {
        stage('Generate Auth Token') {
            steps {
                script {
                    // Replace with your actual API endpoint and credentials
                    def authResponse = httpRequest(
                        url: 'https://dev-api2.augmedix.com/auth/v1/token?idp=com.augmedix.legacy&grantType=password',
                        httpMode: 'POST',
                        contentType: 'APPLICATION_JSON',
                        requestBody: '{"username": "sai_lynx_hca@augmedix.com", "password": "#UgMed1x@"}'
                    )
                    def authJson = readJSON text: authResponse.content
                    env.AUTH_TOKEN = authJson.token // Set the token as an environment variable
                    echo "Auth token generated successfully."
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    def parallelTestConfiguration = [
                        '[Appointments]': 'testcases/test_appointments',
                        '[Audio Continuity]': 'testcases/test_audio_continuity',
                        '[Commure Templates]': 'testcases/test_commure_template',
                        '[Recording Process]': 'testcases/test_recording_process',
                        '[Transcript]': 'testcases/test_transcript'
                    ]

                    def stepList = prepareBuildStages(parallelTestConfiguration)

                    for (def groupOfSteps in stepList) {
                        parallel groupOfSteps
                    }
                }
            }
        }
    }
}

def prepareBuildStages(List<Map<String,String>> parallelTestConfiguration) {
    def stepList = []

    println('Preparing builds...')

    for (def parallelConfig in parallelTestConfiguration) {
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
    } else {
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
                rm -rf ${WORKSPACE}/allure-results && \
                AUTH_TOKEN=${env.AUTH_TOKEN} python3 -m pytest --env=${ENV.toLowerCase()} ${file}.py -m ${TESTTYPE.toLowerCase()} \
                --junitxml=${WORKSPACE}/testResults/${file}.xml --enable-jenkins=yes --alluredir=${WORKSPACE}/allure-results -rA
                """
            }
        }
    }
}
