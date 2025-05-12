pipeline {
    agent any

    environment {
        GIT_CREDENTIALS = 'google-gmail'
        DOCKER_IMAGE_FRONTEND = 'priyansh2000/frontend-app'
        DOCKER_IMAGE_BACKEND = 'priyansh2000/backend-app'
        DOCKER_TAG = "${env.BUILD_NUMBER}"
        KUBECONFIG_FILE = credentials('kube-config')
        KUBECONFIG_PATH = "${WORKSPACE}/.kube/config"
        MINIKUBE_CERTS_DIR = "${WORKSPACE}/.minikube"
    }

    stages {
        stage('Clone Repository') {
            steps {
                git(
                    url: 'https://github.com/priyansh2000/spedemo2.git',
                    credentialsId: 'google-gmail',
                    poll: true
                )
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    sh 'python3 -m venv venv-backend'
                    sh '. venv-backend/bin/activate && pip install -r backend/requirements.txt'
                    sh '. venv-backend/bin/activate && pip install pytest'

                    sh 'python3 -m venv venv-frontend'
                    sh '. venv-frontend/bin/activate && pip install -r frontend/requirements.txt'
                    sh '. venv-frontend/bin/activate && pip install pytest'
                }
            }
        }

        stage('Build Docker Images') {
            steps {
                script {
                    sh """
                    docker build \
                        --no-cache \
                        --build-arg BUILD_NUMBER=${env.BUILD_NUMBER} \
                        -t ${DOCKER_IMAGE_FRONTEND}:${DOCKER_TAG} \
                        -t ${DOCKER_IMAGE_FRONTEND}:latest \
                        ./frontend
                    """
                    sh """
                    docker build \
                        --no-cache \
                        --build-arg BUILD_NUMBER=${env.BUILD_NUMBER} \
                        -t ${DOCKER_IMAGE_BACKEND}:${DOCKER_TAG} \
                        -t ${DOCKER_IMAGE_BACKEND}:latest \
                        ./backend
                    """
                }
            }
        }

        stage('Push Docker Images') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'DockerHubCred',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    script {
                        sh 'echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin'
                        sh "docker push ${DOCKER_IMAGE_FRONTEND}:${DOCKER_TAG}"
                        sh "docker push ${DOCKER_IMAGE_FRONTEND}:latest"
                        sh "docker push ${DOCKER_IMAGE_BACKEND}:${DOCKER_TAG}"
                        sh "docker push ${DOCKER_IMAGE_BACKEND}:latest"
                    }
                }
            }
        }

        stage('Prepare Kubeconfig and Certificates') {
            steps {
                script {
                    sh "mkdir -p ${MINIKUBE_CERTS_DIR}/profiles/minikube"
                    sh "mkdir -p ${WORKSPACE}/.kube"

                    withCredentials([
                        file(credentialsId: 'minikube-client-cert', variable: 'CLIENT_CERT'),
                        file(credentialsId: 'minikube-client-key', variable: 'CLIENT_KEY'),
                        file(credentialsId: 'minikube-ca', variable: 'CA_CRT'),
                        file(credentialsId: 'kube-config', variable: 'KUBECONFIG_FILE')
                    ]) {
                        sh "cp '$CLIENT_CERT' ${MINIKUBE_CERTS_DIR}/profiles/minikube/client.crt"
                        sh "cp '$CLIENT_KEY' ${MINIKUBE_CERTS_DIR}/profiles/minikube/client.key"
                        sh "cp '$CA_CRT' ${MINIKUBE_CERTS_DIR}/ca.crt"

                        sh "cp '$KUBECONFIG_FILE' ${KUBECONFIG_PATH}"
                        sh """
                        sed -i 's|/home/prabhav/.minikube/profiles/minikube/client.crt|${MINIKUBE_CERTS_DIR}/profiles/minikube/client.crt|g' ${KUBECONFIG_PATH}
                        sed -i 's|/home/prabhav/.minikube/profiles/minikube/client.key|${MINIKUBE_CERTS_DIR}/profiles/minikube/client.key|g' ${KUBECONFIG_PATH}
                        sed -i 's|/home/prabhav/.minikube/ca.crt|${MINIKUBE_CERTS_DIR}/ca.crt|g' ${KUBECONFIG_PATH}
                        """

                        sh "chmod 644 ${MINIKUBE_CERTS_DIR}/profiles/minikube/client.crt"
                        sh "chmod 600 ${MINIKUBE_CERTS_DIR}/profiles/minikube/client.key"
                        sh "chmod 644 ${MINIKUBE_CERTS_DIR}/ca.crt"
                        sh "chmod 600 ${KUBECONFIG_PATH}"
                    }

                    sh "KUBECONFIG=${KUBECONFIG_PATH} kubectl cluster-info"
                }
            }
        }

        stage('Deploy using Ansible') {
            steps {
                script {
                    sh """
                    ansible-playbook -i localhost, ansible/playbook.yml \
                        --extra-vars kubeconfig_path=${KUBECONFIG_PATH} \
                        --extra-vars frontend_image_tag=${DOCKER_TAG} \
                        --extra-vars backend_image_tag=${DOCKER_TAG}
                    """
                }
            }
        }
    }

    post {
        always {
            script {
                cleanWs()
            }
        }
        success {
            emailext(
                to: 'iam49smith@gmail.com',
                subject: "SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """<p>The build and deployment were <b>successful!</b></p>
                         <p>Check the build details: <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>"""
            )
        }
        failure {
            emailext(
                to: 'iam49smith@gmail.com',
                subject: "FAILURE: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: """<p>The build or deployment <b>failed!</b></p>
                         <p>Check the build details: <a href="${env.BUILD_URL}">${env.BUILD_URL}</a></p>"""
            )
        }
    }

}
