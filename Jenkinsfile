// Glow Services - AI-Native Pipeline
// Jenkinsfile (Declarative Pipeline)

pipeline {
    agent any
    
    environment {
        DOTNET_VERSION = '8.0'
        DOCKER_REGISTRY = 'ghcr.io/glow-services'
        IMAGE_NAME = 'glow-claims-api'
        OPENAI_API_KEY = credentials('openai-api-key')
        AZURE_CREDENTIALS = credentials('azure-service-principal')
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }
    
    stages {
        // ============================================================
        // PHASE 1: PRD → SPECIFICATION
        // ============================================================
        stage('📋 PRD → Specification') {
            agent {
                docker { image 'python:3.11' }
            }
            steps {
                sh '''
                    pip install openai langchain pydantic jsonschema
                    python scripts/prd_to_spec.py \
                        --input specs/claims-auto-approval.json \
                        --output specs/generated/
                    python scripts/validate_spec.py specs/generated/specification.json
                '''
            }
            post {
                success {
                    archiveArtifacts artifacts: 'specs/generated/**', fingerprint: true
                }
            }
        }
        
        // ============================================================
        // PHASE 2: SPECIFICATION → CODE
        // ============================================================
        stage('⚡ Specification → Code') {
            agent {
                docker { image 'python:3.11' }
            }
            steps {
                sh '''
                    pip install openai langchain jinja2
                    python scripts/spec_to_code.py \
                        --spec specs/generated/specification.json \
                        --output src/Generated/
                    python scripts/generate_tests.py \
                        --spec specs/generated/specification.json \
                        --code src/Generated/ \
                        --output tests/Generated/
                '''
            }
            post {
                success {
                    archiveArtifacts artifacts: 'src/Generated/**, tests/Generated/**', fingerprint: true
                }
            }
        }
        
        // ============================================================
        // PHASE 3: AI CODE REVIEW
        // ============================================================
        stage('🤖 AI Code Review') {
            agent {
                docker { image 'python:3.11' }
            }
            steps {
                sh '''
                    pip install openai
                    python scripts/ai_code_review.py \
                        --code src/Generated/ \
                        --checklist "security,compliance,quality" \
                        --output review-report.json
                '''
                script {
                    def review = readJSON file: 'review-report.json'
                    if (review.critical_issues?.size() > 0) {
                        error "Critical issues found in AI review"
                    }
                    echo "Security Score: ${review.security_score}/100"
                    echo "Quality Score: ${review.quality_score}/100"
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'review-report.json'
                }
            }
        }
        
        // ============================================================
        // PHASE 4: QUALITY GATES
        // ============================================================
        stage('🛡️ Quality Gates') {
            parallel {
                stage('Build & Test') {
                    agent {
                        docker { image 'mcr.microsoft.com/dotnet/sdk:8.0' }
                    }
                    steps {
                        sh '''
                            dotnet restore
                            dotnet build --configuration Release
                            dotnet test --configuration Release \
                                --collect:"XPlat Code Coverage" \
                                --results-directory ./coverage \
                                --logger "trx;LogFileName=test-results.trx"
                        '''
                    }
                    post {
                        always {
                            junit 'coverage/**/*.trx'
                            publishCoverage adapters: [coberturaAdapter('coverage/**/coverage.cobertura.xml')]
                        }
                    }
                }
                
                stage('Security Scan') {
                    agent {
                        docker { image 'mcr.microsoft.com/dotnet/sdk:8.0' }
                    }
                    steps {
                        sh 'dotnet list package --vulnerable --include-transitive'
                    }
                }
                
                stage('SAST') {
                    agent {
                        docker { image 'returntocorp/semgrep' }
                    }
                    steps {
                        sh 'semgrep --config auto --json --output sast-report.json src/ || true'
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'sast-report.json'
                        }
                    }
                }
                
                stage('Prompt Regression') {
                    agent {
                        docker { image 'python:3.11' }
                    }
                    steps {
                        sh '''
                            pip install openai
                            python scripts/prompt_regression.py \
                                --golden-tests tests/golden/ \
                                --threshold 0.95 \
                                --output regression-report.json
                        '''
                    }
                }
            }
        }
        
        // ============================================================
        // PHASE 5: BUILD CONTAINER
        // ============================================================
        stage('📦 Build Container') {
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-credentials') {
                        def image = docker.build("${IMAGE_NAME}:${env.GIT_COMMIT}")
                        image.push()
                        image.push('latest')
                    }
                }
            }
        }
        
        // ============================================================
        // PHASE 6: DEPLOY STAGING
        // ============================================================
        stage('🚀 Deploy Staging') {
            steps {
                withCredentials([azureServicePrincipal('azure-service-principal')]) {
                    sh '''
                        az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID
                        az containerapp update \
                            --name glow-claims-staging \
                            --resource-group glow-rg-staging \
                            --image ${DOCKER_REGISTRY}/${IMAGE_NAME}:${GIT_COMMIT}
                    '''
                }
            }
        }
        
        stage('🧪 Smoke Tests') {
            steps {
                sh '''
                    sleep 30
                    curl -f https://staging.glow-claims.com/health || exit 1
                    
                    RESPONSE=$(curl -s -X POST \
                        https://staging.glow-claims.com/api/v1/claims/screen-damage/approve \
                        -H "Content-Type: application/json" \
                        -d '{"claim_amount_gbp": 150, "damage_type": "SCREEN", "risk_score": 0.2}')
                    
                    STATUS=$(echo $RESPONSE | jq -r '.status')
                    [ "$STATUS" = "APPROVED" ] || exit 1
                    echo "✅ Smoke tests passed"
                '''
            }
        }
        
        // ============================================================
        // PHASE 7: DEPLOY PRODUCTION (Manual Gate)
        // ============================================================
        stage('🎯 Deploy Production') {
            when {
                branch 'main'
            }
            input {
                message "Deploy to production?"
                ok "Deploy"
            }
            steps {
                withCredentials([azureServicePrincipal('azure-service-principal')]) {
                    sh '''
                        az login --service-principal -u $AZURE_CLIENT_ID -p $AZURE_CLIENT_SECRET --tenant $AZURE_TENANT_ID
                        az containerapp update \
                            --name glow-claims-prod \
                            --resource-group glow-rg-prod \
                            --image ${DOCKER_REGISTRY}/${IMAGE_NAME}:${GIT_COMMIT}
                    '''
                }
            }
        }
        
        // ============================================================
        // PHASE 8: POST-DEPLOYMENT
        // ============================================================
        stage('📊 Post-Deploy Monitor') {
            when {
                branch 'main'
            }
            steps {
                sh '''
                    sleep 60
                    curl -f https://api.glow-claims.com/health || exit 1
                    echo "✅ Production deployment verified"
                '''
            }
        }
    }
    
    post {
        success {
            slackSend(
                color: 'good',
                message: "✅ Pipeline SUCCESS: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
            )
        }
        failure {
            slackSend(
                color: 'danger',
                message: "❌ Pipeline FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}"
            )
        }
    }
}
