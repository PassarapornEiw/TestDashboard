pipeline {
    agent any
    
    environment {
        PROJECT_NAME = 'Test Dashboard'
        PROJECT_PATH = '/opt/Test Dashboard'
        SERVICE_NAME = 'test-dashboard'
        AUTOMATION_PROJECT_PATH = '/opt/Automation Project'
        RESULTS_PATH = '/opt/Automation Project/results'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Test') {
            steps {
                script {
                    // Run tests if you have them
                    echo "Running tests..."
                    // sh 'python -m pytest tests/'
                }
            }
        }
        
        stage('Deploy') {
            steps {
                script {
                    echo "Deploying to production server..."
                    
                    // Copy files to server (if Jenkins is on different machine)
                    // sh "scp -r . jenkins@your-server:/opt/$PROJECT_NAME/"
                    
                    // Or if Jenkins is on the same machine
                    sh "sudo systemctl stop $SERVICE_NAME"
                    sh "cd $PROJECT_PATH && git pull origin main"
                    sh "source $PROJECT_PATH/venv/bin/activate && pip install -r requirements.txt"
                    sh "sudo chown -R jenkins:jenkins $PROJECT_PATH"
                    sh "sudo systemctl daemon-reload"
                    sh "sudo systemctl start $SERVICE_NAME"
                }
            }
        }
        
        stage('Verify') {
            steps {
                script {
                    echo "Verifying deployment..."
                    sh "sleep 10" // Wait for service to start
                    sh "curl -f http://localhost:5000/api/data || exit 1"
                    echo "✅ Deployment verified successfully!"
                }
            }
        }
    }
    
    post {
        always {
            echo "Deployment pipeline completed"
        }
        failure {
            echo "Deployment failed! Check logs and service status"
            sh "sudo systemctl status $SERVICE_NAME"
        }
    }
}
