pipeline {
    agent any
    
    environment {
        PYTHON_PATH = 'C:\\Users\\Kopikou\\Desktop\\study\\Devops\\todo-app\\.conda\\python.exe'
        PROJECT_PATH = 'C:\\Users\\Kopikou\\Desktop\\study\\Devops\\todo-app'
        PRODUCTION_PATH = 'C:\\Users\\Kopikou\\Desktop\\study\\Devops\\todo-app-production'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo "Checking out code from ${env.GIT_BRANCH}"
                checkout scm
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo "Running unit tests..."
                bat """
                    \"${env.PYTHON_PATH}\" -m pip install -r requirements.txt
                    \"${env.PYTHON_PATH}\" -m pytest tests/ -v
                """
            }
        }
        
        stage('Test Report for Dev') {
            when {
                branch 'dev'
            }
            steps {
                echo "Generating test report for dev branch..."
                bat """
                    \"${env.PYTHON_PATH}\" -m pytest tests/ -v > test-report.txt
                """
                archiveArtifacts artifacts: 'test-report.txt', fingerprint: true
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                echo "Deploying to production..."
                bat """
                    rmdir /s /q \"${env.PRODUCTION_PATH}\" 2>nul
                    mkdir \"${env.PRODUCTION_PATH}\"
                    
                    xcopy .\\* \"${env.PRODUCTION_PATH}\" /Y /I /E
                    
                    echo "Production version: ${env.GIT_COMMIT}"
                """
            }
        }
    }
    
    post {
        always {
            echo "Pipeline execution completed for branch: ${env.GIT_BRANCH}"
        }
        success {
            script {
                if (env.GIT_BRANCH == 'origin/dev') {
                    echo "CI process completed successfully for dev branch"
                } else if (env.GIT_BRANCH == 'origin/main') {
                    echo "CD process completed successfully for main branch"
            }
        }
        failure {
            echo "Pipeline execution failed"
        }
    }
}