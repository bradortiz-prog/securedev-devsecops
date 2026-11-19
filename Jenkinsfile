pipeline {
    agent any

    environment {
        APP_NAME = "securedev-web"
        IMAGE_NAME = "securedev-app:latest"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build - Construccion Docker') {
            steps {
                sh 'docker build -t ${IMAGE_NAME} .'
            }
        }

        stage('Deploy - Despliegue en Produccion') {
            steps {
                sh '''
                docker stop ${APP_NAME} || true
                docker rm ${APP_NAME} || true
                docker run -d --name ${APP_NAME} --network devsecops-net -p 5000:5000 ${IMAGE_NAME}
                sleep 5
                '''
            }
        }

        stage('Security Test - OWASP ZAP') {
            steps {
                sh '''
                chmod 777 .
                docker run --rm --network devsecops-net -v $(pwd):/zap/wrk/:rw ghcr.io/zaproxy/zaproxy:stable zap-baseline.py -t http://${APP_NAME}:5000 -r reporte_zap.html || true
                '''
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reporte_zap.html', allowEmptyArchive: true
        }
    }
}