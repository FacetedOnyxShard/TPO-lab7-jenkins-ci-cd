pipeline {
    agent any
    
    stages {
        stage('Подготовка') {
            steps {
                sh '''
                    echo "Проверяем файлы..."
                    ls -la > preparation_files.txt
                    ls -la chromedriver-linux64/ > chromedriver_files.txt
                    
                    echo "Устанавливаем зависимости..."
                    pip3 install selenium requests pytest locust urllib3 > dependencies.log 2>&1
                    
                    echo "Даем права на выполнение..."
                    chmod +x runbmc.sh
                    chmod +x chromedriver-linux64/chromedriver
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'preparation_files.txt, chromedriver_files.txt, dependencies.log'
                }
            }
        }
        
        stage('Запуск QEMU') {
            steps {
                sh '''
                    echo "Запускаем QEMU с OpenBMC..."
                    echo "Проверяем romulus..."
                    ls -la /romulus/ > romulus_files.txt
                    
                    ./runbmc.sh > qemu_boot.log 2>&1 &
                    echo "QEMU запущен, ждем 120 секунд..."
                    sleep 120
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'romulus_files.txt, qemu_boot.log'
                }
            }
        }
        
        stage('API тесты') {
            steps {
                sh '''
                    echo "Запуск API тестов..."
                    python3 openbmc_test.py > openbmc_test.log 2>&1
                    python3 -m pytest redfish_api_auth_test.py -v --junitxml=api_test_results.xml > api_tests.log 2>&1
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'openbmc_test.log, api_tests.log, api_test_results.xml'
                    junit 'api_test_results.xml'
                }
            }
        }
        
        stage('WebUI тесты') {
            steps {
                sh '''
                    echo "Запуск WebUI тестов..."
                    python3 openbmc_auth_test.py > webui_tests.log 2>&1
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'webui_tests.log'
                }
            }
        }
        
        stage('Нагрузочное тестирование') {
            steps {
                sh '''
                    echo "Запуск нагрузочного тестирования..."
                    timeout 60 locust -f locustfile_redfish_api.py --headless -u 1 -r 1 -t 30s --host=https://localhost:2443 --html=load_report.html > load_test.log 2>&1
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
            sh '''
                echo "Останавливаем QEMU..."
                pkill -f qemu-system-arm || true
            '''
            archiveArtifacts artifacts: '**/*.log, **/*.txt, **/*.xml, **/*.html'
        }
    }
}