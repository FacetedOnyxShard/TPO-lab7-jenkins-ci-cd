pipeline {
    agent any
    
    stages {
    stage('Start QEMU with OpenBMC') {
      steps {
        script {
          sh """
            ./scripts/start_qemu.sh
          """
        }
      }
    }

    stage('Wait for BMC Startup') {
      steps {
        script {
          timeout(time: 5, unit: 'MINUTES') {
            waitUntil {
              try {
                sh """
                  nc -z localhost 2222 && nc -z localhost 2443
                """
                return true
              } catch (Exception e) {
                echo "Waiting for BMC to start... (ports not ready yet)"
                sleep 10
                return false
              }
            }
          }
        }
      }
    }
        
        stage('Run Autotests') {
            steps {
                sh '''
                    pip3 install selenium requests pytest locust urllib3 
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
                    timeout 120 locust -f locustfile_redfish_api.py --headless -u 10 -r 2 -t 90s --host=https://localhost:2443 --html=load_report.html > load_test.log 2>&1
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