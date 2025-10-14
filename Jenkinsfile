pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = 'docker.io/kopikou'  // Например: docker.io/yourusername
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
                    sh "docker build -t ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-app:${env.BUILD_NUMBER} ."
                    
                    // Сборка образа nginx
                    sh "docker build -t ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-nginx:${env.BUILD_NUMBER} -f Dockerfile.nginx ."
                }
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo "Running unit tests in container..."
                script {
                    // Запуск тестов в контейнере
                    sh """
                    docker run --rm \
                        ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-app:${env.BUILD_NUMBER} \
                        python -m pytest tests/ -v
                    """
                }
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
                        sh """
                        docker login -u $DOCKER_USER -p $DOCKER_PASS ${env.DOCKER_REGISTRY}
                        docker push ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-app:${env.BUILD_NUMBER}
                        docker push ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-nginx:${env.BUILD_NUMBER}
                        
                        // Также пушим latest теги
                        docker tag ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-app:${env.BUILD_NUMBER} ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-app:latest
                        docker tag ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-nginx:${env.BUILD_NUMBER} ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-nginx:latest
                        docker push ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-app:latest
                        docker push ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-nginx:latest
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
                    sh """
                    // Останавливаем и удаляем старые контейнеры
                    docker-compose down || true
                    
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
                    sh 'sleep 30'
                    
                    // Проверяем доступность приложения
                    sh """
                    curl -f http://localhost:80/ || exit 1
                    curl -f http://localhost:80/api/todos || exit 1
                    """
                }
            }
        }
    }
    
    post {
        always {
            echo "Pipeline execution completed for branch: ${env.GIT_BRANCH}"
            script {
                // Очистка: удаляем локальные образы для экономии места
                if (env.GIT_BRANCH != 'origin/main') {
                    sh """
                    docker rmi ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-app:${env.BUILD_NUMBER} || true
                    docker rmi ${env.DOCKER_REGISTRY}/${env.PROJECT_NAME}-nginx:${env.BUILD_NUMBER} || true
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
            sh 'docker image prune -f'
        }
    }
}