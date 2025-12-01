pipeline {
    agent any
    
    stages {
        stage('Start Qemu') {
            steps {
                sh '''
                    ./start_qemu.sh > qemu_boot.log 2>&1 &
                '''

                timeout(time: 5, unit: 'MINUTES') {
                    waitUntil {
                    try {
                        sh """
                            nc -z localhost 2222 && nc -z localhost 2443
                        """
                        return true
                    } catch (Exception e) {
                        echo "Waiting for BMC to start... (ports not ready yet)"
                        sleep 30
                        return false
                    }
                }
          }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'qemu_openbmc_boot.log'
                }
            }
        }
        
        stage('Run Autotests') {
            steps {
                sh '''
                    echo "Start API tests..."
                    python3 -m pytest redfish_api.py -v --junitxml=api_test_results.xml > api_tests.log 2>&1
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'api_tests.log, api_test_results.xml'
                    junit 'api_test_results.xml'
                }
            }
        }
        
        stage('WebUI tests') {
            steps {
                sh '''
                    echo "Start WebUI tests..."
                    python3 webui_tests.py > webui_tests_logs.txt 2>&1
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'webui_tests_logs.txt'
                }
            }
        }
        
        stage('Load testing') {
            steps {
                sh '''
                    echo "Start loading testing..."
                    timeout 60 locust -f locustfile.py --headless -u 1 -r 1 -t 30s --host=https://localhost:2443 --html=load_report.html > load_test.log 2>&1
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