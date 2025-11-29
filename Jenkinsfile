pipeline {
    agent any
    
    stages {
    stage('Start QEMU with OpenBMC') {
      steps {
        script {
          sh """
            ./start_qemu.sh
          """
        }
      }
    }

    stage('Wait for BMC Startup') {
      steps {
        script {
          sh 'sleep 120'
        }
      }
    }
        
        stage('Run Autotests') {
            steps {
                sh '''
                    python3 -m pytest test_redfish.py -v > api_tests.log 2>&1
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'api_tests.log'
                }
            }
        }
        
        stage('WebUI tests') {
            steps {
                sh '''
                  python3 -m pytest test_openbmc_auth_tests.py > webui_tests.log 2>&1
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'webui_tests.log'
                }
            }
        }
        
        stage('Load testing') {
            steps {
                sh '''
                    timeout 60 locust -f locustfile.py --headless -u 10 -r 2 -t 30s --host=https://localhost:2443 --html=load_report.html > load_test.log 2>&1
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'load_report.html, load_test.log'
                }
            }
        }
    }
    
    post {
        always {
            script {
                def pid = sh(
                    script: """
                        ps aux | grep qemu | grep -v grep | awk '{print \$2}' || echo ""
                    """,
                    returnStdout: true
                ).trim()

                if (pid) {
                    echo "QEMU PID found: ${pid}"
                    sh "kill ${pid}"
                } else {
                    echo "No QEMU process found"
                }
            }
        }
    }
}