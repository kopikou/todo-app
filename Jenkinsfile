pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'docker.io/kopikou'  
        PROJECT_NAME = 'todo-app'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo "Checking out code from ${env.GIT_BRANCH}"
                checkout scm
            }
        }
        
        stage('Build Docker Images') {
            steps {
                echo "Building Docker images..."
                script {
                    // Сборка образа приложения
                    bat """
                    docker build -t ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-app:${env.BUILD_NUMBER} .
                    """
                    
                    // Сборка образа nginx
                    bat """
                    docker build -t ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-nginx:${env.BUILD_NUMBER} -f Dockerfile.nginx .
                    """
                }
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo "Running unit tests in container..."
                script {
                    // Запуск тестов в контейнере
                    bat """
                    docker run --rm ^
                        ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-app:${env.BUILD_NUMBER} ^
                        python -m pytest tests/ -v
                    """
                }
            }
        }
        
        stage('Test Report for Dev') {
            when {
                expression { env.GIT_BRANCH == 'origin/dev' }
            }
            steps {
                echo "Generating test report for dev branch..."
                bat """
                    docker run --rm ^
                        ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-app:${env.BUILD_NUMBER} ^
                        python -m pytest tests/ -v > test-report.txt
                """
                archiveArtifacts artifacts: 'test-report.txt', fingerprint: true
            }
        }
        
        stage('Push to Registry') {
            when {
                expression { env.GIT_BRANCH == 'origin/main' }
            }
            steps {
                echo "Pushing images to container registry..."
                script {
                    withCredentials([usernamePassword(
                        credentialsId: 'docker-registry-creds',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )]) {
                        bat """
                        docker login -u %DOCKER_USER% -p %DOCKER_PASS% ${env.DOCKER_REGISTRY}
                        docker push ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-app:${env.BUILD_NUMBER}
                        docker push ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-nginx:${env.BUILD_NUMBER}
                        
                        """
                    }
                }
            }
        }
        
        stage('Deploy to Production') {
            when {
                expression { env.GIT_BRANCH == 'origin/main' }
            }
            steps {
                echo "Deploying to production..."
                script {
                    bat """
                    // Останавливаем и удаляем старые контейнеры
                    docker-compose down || echo "No running containers found"
                    
                    // Запускаем новые контейнеры
                    docker-compose up -d
                    
                    echo "Production deployed with version: ${env.BUILD_NUMBER}"
                    """
                }
            }
        }
        
        stage('Integration Test') {
            when {
                expression { env.GIT_BRANCH == 'origin/main' }
            }
            steps {
                echo "Running integration tests..."
                script {
                    // Ждем пока приложение поднимется
                    bat 'ping -n 30 127.0.0.1 > nul'
                    
                    // Проверяем статус контейнеров
                    bat 'docker-compose ps'
                    
                    // Проверяем логи приложения
                    bat 'docker-compose logs app'
                    
                    // Проверка доступности 
                    bat """
                    curl -s -o nul -w "%%{http_code}" http://localhost/ | find "200" && (
                        echo "Application is responding successfully"
                    ) || (
                        echo "Application not ready yet, but continuing deployment"
                    )
                    """
                    bat """
                    curl -f http://localhost:80/ || exit /b 1
                    curl -f http://localhost:80/api/todos || exit /b 1
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo "Pipeline execution completed for branch: ${env.GIT_BRANCH}"
            script {
                // удаляем локальные образы 
                if (env.GIT_BRANCH != 'origin/main') {
                    bat """
                    docker rmi ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-app:${env.BUILD_NUMBER} || echo "Image not found"
                    docker rmi ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-nginx:${env.BUILD_NUMBER} || echo "Image not found"
                    """
                }
            }
        }
        success {
            script {
                if (env.GIT_BRANCH == 'origin/dev') {
                    echo "CI process completed successfully for dev branch"
                } else if (env.GIT_BRANCH == 'origin/main') {
                    echo "CD process completed successfully for main branch"
                    echo "Docker images pushed to registry:"
                    echo "- ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-app:${env.BUILD_NUMBER}"
                    echo "- ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-nginx:${env.BUILD_NUMBER}"
                }
            }
        }
        failure {
            echo "Pipeline execution failed"
        }
        cleanup {
            // Очистка dangling images 
            bat 'docker image prune -f'
        }
    }
}