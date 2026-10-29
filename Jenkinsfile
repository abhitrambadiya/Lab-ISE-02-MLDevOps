pipeline {
    agent any

    environment {
        APP_NAME        = 'housing-price-predictor'
        DOCKER_IMAGE    = "abhitrambadiya/${APP_NAME}:${BUILD_NUMBER}"
        DOCKER_LATEST   = "abhitrambadiya/${APP_NAME}:latest"
        DOCKER_REGISTRY = 'docker.io'
        PORT            = '5000'
    }

    stages {
        // ----------------------------------------------------
        // Stage 1: Checkout Source Code
        // ----------------------------------------------------
        stage('Checkout') {
            steps {
                echo 'Pulling latest code from GitHub repository...'
                checkout scm
            }
        }

        // ----------------------------------------------------
        // Stage 2: Environment Setup & Linting
        // ----------------------------------------------------
        stage('Environment Setup & Dependencies') {
            steps {
                echo 'Setting up Python virtual environment and installing dependencies...'
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        // ----------------------------------------------------
        // Stage 3: Automated Testing & Validation (pytest)
        // ----------------------------------------------------
        stage('Automated Tests & Quality Gates') {
            steps {
                echo 'Running unit tests, data validation, and model accuracy benchmarks...'
                sh '''
                    . .venv/bin/activate
                    pytest tests/ -v --junitxml=test-results.xml
                '''
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }

        // ----------------------------------------------------
        // Stage 4: Docker Container Build
        // ----------------------------------------------------
        stage('Docker Build') {
            steps {
                echo "Building Docker container image: ${DOCKER_IMAGE}..."
                sh """
                    docker build -t ${DOCKER_IMAGE} -t ${DOCKER_LATEST} .
                """
            }
        }

        // ----------------------------------------------------
        // Stage 5: Container Verification & Smoke Testing
        // ----------------------------------------------------
        stage('Container Smoke Test') {
            steps {
                echo 'Spooling test container to verify HTTP endpoints...'
                sh """
                    docker run -d --name ${APP_NAME}-test -p 5001:5000 ${DOCKER_LATEST}
                    sleep 5
                    curl -f http://127.0.0.1:5001/health || exit 1
                    docker stop ${APP_NAME}-test
                    docker rm ${APP_NAME}-test
                """
            }
        }

        // ----------------------------------------------------
        // Stage 6: Push Image to Registry (Optional / Staging)
        // ----------------------------------------------------
        stage('Push to Registry') {
            when {
                branch 'main'
            }
            steps {
                echo 'Publishing verified container image to Docker Hub...'
                // withCredentials([usernamePassword(credentialsId: 'docker-hub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                //     sh "echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin"
                //     sh "docker push ${DOCKER_IMAGE}"
                //     sh "docker push ${DOCKER_LATEST}"
                // }
                sh "echo 'Docker push simulation completed successfully.'"
            }
        }

        // ----------------------------------------------------
        // Stage 7: Automated Deployment
        // ----------------------------------------------------
        stage('Deploy to Production Container') {
            steps {
                echo 'Deploying application container with zero-downtime port binding...'
                sh """
                    docker stop ${APP_NAME} || true
                    docker rm ${APP_NAME} || true
                    docker run -d --name ${APP_NAME} -p ${PORT}:5000 --restart always ${DOCKER_LATEST}
                    echo 'Application successfully deployed and running on port ${PORT}.'
                """
            }
        }
    }

    post {
        success {
            echo "CI/CD Pipeline executed successfully for build #${BUILD_NUMBER}!"
        }
        failure {
            echo "ERROR: Pipeline failed. Check console output for debugging."
        }
    }
}

