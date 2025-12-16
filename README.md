# Glow Services | AI-Native Pipeline

> **PRD → Code → Deployment** in production using GitHub Actions, GitLab CI/CD, or Jenkins

## Overview

This repository demonstrates an **AI-Native CI/CD Pipeline** that:

1. **Converts PRD → Structured Specification** (LLM-powered)
2. **Generates Production Code** (Python Flask API)
3. **AI Code Review** (Security, Compliance, Quality) - Optional
4. **Automated Testing** (pytest, Prompt Regression) - Optional
5. **Container Build & Deploy** (Staging → Production) - Optional
6. **Post-Deployment Monitoring** (Drift Detection) - Optional

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│     PRD     │───▶│    SPEC     │───▶│    CODE     │───▶│  QUALITY    │
│  (JSON/MD)  │    │ (Structured)│    │   (Python)  │    │   GATES     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │                  │
       ▼                  ▼                  ▼                  ▼
   LLM Parse         LLM Generate       Syntax Check        Preview Code
   + Validate        + Tests            + Validation        + Demo Ready
```

**Current Demo Focus:** Core pipeline (PRD → Spec → Python Code → Validation)
**Optional Features:** Testing, security scans, deployment (can be re-enabled)

## Quick Start

### 1. Folder Structure

```
C:\Users\ELITEBOOK\OneDrive\Desktop\Projects\
├── .env                    ← secrets here (OUTSIDE project)
└── glow_prd\               ← project here
    ├── scripts\
    ├── specs\
    ├── src\
    └── ...
```

**Why?** Keeps `.env` outside the project so AI tools can't access your API keys.

### 2. Create `.env` File

Create this file:
```
C:\Users\ELITEBOOK\OneDrive\Desktop\Projects\.env
```

Add your keys:
```env
OPENAI_API_KEY=sk-your-key-here

# Optional - for Azure deployment
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
AZURE_TENANT_ID=
AZURE_SUBSCRIPTION_ID=
```

### 3. Setup Project

```bash
cd C:\Users\ELITEBOOK\OneDrive\Desktop\Projects\glow_prd

# Install dependencies
pip install -r requirements.txt
```

### 4. Test

**Windows PowerShell:**
```powershell
.\test.ps1
```

**Windows Command Prompt:**
```cmd
test.bat
```

**Linux/Mac:**
```bash
make test
```

You'll see:
```
📁 Loading config from: C:\Users\ELITEBOOK\OneDrive\Desktop\Projects\.env
✅ Configuration loaded successfully
[1/4] PRD -> Specification
Done: specs\generated\specification.json
...
All Tests Passed!
```

### 5. CI/CD Secrets

For GitHub/GitLab/Jenkins, set secrets in the platform (not in .env):

```bash
# GitHub Actions
gh secret set OPENAI_API_KEY --body "sk-..."
```

```json
// specs/my-feature.json
{
  "id": "PRD-001",
  "title": "Auto-Approval Claims",
  "business_requirement": {
    "summary": "Auto-approve screen damage claims under £250"
  },
  "constraints": {
    "max_claim_amount_gbp": 250.00,
    "max_risk_score": 0.3
  }
}
```

### 6. Run Pipeline

```bash
git add specs/my-feature.json
git commit -m "feat: add auto-approval"
git push
```

---

## Pipeline Files

| File | Platform | Description |
|------|----------|-------------|
| `.github/workflows/ai-native-pipeline.yml` | GitHub Actions | Full 9-stage pipeline |
| `.gitlab-ci.yml` | GitLab CI/CD | Equivalent GitLab pipeline |
| `Jenkinsfile` | Jenkins | Declarative Jenkins pipeline |

---

## Pipeline Stages

### Stage 1: PRD → Specification
Converts business requirements into machine-readable specs.

```bash
python scripts/prd_to_spec.py --input specs/claims.json --output specs/generated/
```

**Output:** `specs/generated/specification.json`
```json
{
  "api_contract": { "method": "POST", "endpoint": "/api/v1/claims/..." },
  "decision_rules": [
    { "condition": "IF claim <= 250 AND risk <= 0.3", "action": "APPROVE" }
  ],
  "compliance": { "regulations": ["FCA"], "audit_requirements": [...] }
}
```

### Stage 2: Specification → Code
Generates production Python Flask API from specifications.

```bash
python scripts/spec_to_code.py --spec specs/generated/specification.json --output src/generated/
python scripts/generate_tests.py --spec specs/generated/specification.json --output tests/generated/
```

**Output:**
- `src/generated/api.py` - Flask API with routes
- `src/generated/models.py` - Pydantic models
- `tests/generated/test_api.py` - pytest tests

**Run the generated API:**
```bash
pip install flask pydantic
python src/app.py
# API runs at http://localhost:5000
```

### Stage 3: AI Code Review
Automated security, quality, and compliance review.

```bash
python scripts/ai_code_review.py --code src/Generated/ --output review-report.json
```

**Checks:**
- OWASP Top 10 vulnerabilities
- Hardcoded secrets
- PII logging violations
- FCA compliance
- Code quality metrics

### Stage 4: Quality Gates
Standard CI/CD quality checks.

**Demo Configuration (Active):**
| Gate | Tool | Status |
|------|------|--------|
| Syntax Check | python -m py_compile | ✅ Active |
| Code Preview | cat/head | ✅ Active |

**Optional (Can be re-enabled):**
| Gate | Tool | Status |
|------|------|--------|
| Unit Tests | pytest | ⏸️ Disabled for demo |
| Security (SAST) | CodeQL | ⏸️ Disabled for demo |
| Secrets | TruffleHog | ⏸️ Disabled for demo |

### Stage 5: Prompt Regression
Detects logic drift in LLM outputs.

```bash
python scripts/prompt_regression.py --golden-tests tests/golden/ --threshold 0.95
```

### Stage 6-8: Build & Deploy
Container build → Staging → Production with smoke tests.

---

## Directory Structure

```
glow_prd_pipeline/
├── .github/
│   └── workflows/
│       └── ai-native-pipeline.yml    # GitHub Actions pipeline
├── specs/
│   ├── claims-auto-approval.json     # PRD input
│   └── generated/                     # AI-generated specs
├── src/
│   ├── app.py                        # Flask app runner
│   └── generated/                    # AI-generated Python code
│       ├── api.py                    # Flask API endpoints
│       └── models.py                 # Pydantic models
├── tests/
│   └── generated/                    # AI-generated pytest tests
│       └── test_api.py
└── scripts/
    ├── prd_to_spec.py                # PRD → Spec
    ├── spec_to_code.py               # Spec → Python code
    ├── generate_tests.py             # pytest test generator
    ├── validate_spec.py              # Spec schema validator
    └── config.py                     # Config loader
```

---

## Configuration

### Required Secrets

| Secret | Description |
|--------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for code generation |
| `AZURE_CREDENTIALS` | Azure service principal JSON |
| `KUBE_CONFIG` | Kubernetes config (GitLab/Jenkins) |

### Environment Variables

```yaml
DOTNET_VERSION: '8.0.x'
AZURE_WEBAPP_NAME: glow-claims-api
REGISTRY: ghcr.io
```

---

## Key Concepts

### AI-Native vs AI-Augmented

| Aspect | AI-Augmented | AI-Native (This Pipeline) |
|--------|--------------|---------------------------|
| Code Generation | External tool | Pipeline stage |
| Code Review | Add-on | Core gate |
| Test Generation | Manual | Automated from spec |
| Drift Detection | None | Continuous |
| Spec Generation | Manual | LLM-powered |

### What Makes This Production-Ready

1. **Deterministic Specs** - JSON schema validation
2. **Full Audit Trail** - Every decision logged
3. **Quality Gates** - Same standards as human code
4. **Prompt Regression** - Catches model drift
5. **Human-in-the-Loop** - Manual prod deployment gate
6. **Rollback Ready** - Container versioning

---

## Extending the Pipeline

### Add New Feature Type

1. Create PRD template in `specs/templates/`
2. Add decision rules to `scripts/prd_to_spec.py`
3. Add code template to `templates/`

### Custom Quality Gates

```yaml
# .github/workflows/ai-native-pipeline.yml
custom-gate:
  name: Custom Check
  runs-on: ubuntu-latest
  steps:
    - run: ./scripts/custom_check.sh
```

---

## License

Proprietary - Glow Services Corp.

---

## Support

- **Docs:** https://docs.glow-services.com/ai-pipeline
- **Issues:** https://github.com/glow-services/ai-native-pipeline/issues
