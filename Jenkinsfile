// Self-hosted Jenkins pipeline: runs on every commit, deploys only if all tests pass.
pipeline {
  agent any
  environment { DASHBOARD_URL = 'http://localhost:5000' }
  stages {
    stage('Setup') {
      steps {
        sh 'python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt'
      }
    }
    stage('Build sample data + clean') {
      steps {
        sh '. .venv/bin/activate && python generate_sample_data.py && python etl_pipeline.py'
      }
    }
    stage('Backend tests (PyTest)') {
      steps { sh '. .venv/bin/activate && pytest tests/test_etl_pipeline.py tests/test_dashboard_unit.py --junitxml=backend.xml' }
    }
    stage('Frontend tests (Selenium)') {
      steps {
        sh '''. .venv/bin/activate
              python dashboard_app.py & echo $! > app.pid
              sleep 3
              pytest tests/test_dashboard_ui.py --junitxml=ui.xml
              kill $(cat app.pid)'''
      }
    }
    stage('Deploy') {
      steps { echo 'All tests passed: approved for deployment.' }
    }
  }
  post {
    always  { junit '*.xml' }
    failure { echo 'FAIL: alert the developer. Deployment blocked.' }
  }
}
