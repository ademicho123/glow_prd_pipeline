#!/bin/bash
# Glow AI-Native Pipeline - Local Testing Script
# Run: chmod +x test-local.sh && ./test-local.sh

set -e

echo "=========================================="
echo "🧪 Glow AI-Native Pipeline - Local Test"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check prerequisites
check_prereqs() {
    echo -e "\n${YELLOW}1. Checking Prerequisites${NC}"
    
    command -v python3 >/dev/null 2>&1 || { echo -e "${RED}❌ Python 3 required${NC}"; exit 1; }
    command -v docker >/dev/null 2>&1 || { echo -e "${YELLOW}⚠️  Docker not found (optional for container tests)${NC}"; }
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${RED}❌ OPENAI_API_KEY not set${NC}"
        echo "   Run: export OPENAI_API_KEY='sk-...'"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites OK${NC}"
}

# Install dependencies
install_deps() {
    echo -e "\n${YELLOW}2. Installing Dependencies${NC}"
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}✅ Dependencies installed${NC}"
}

# Test Stage 1: PRD → Specification
test_spec_generation() {
    echo -e "\n${YELLOW}3. Testing PRD → Specification${NC}"
    
    mkdir -p specs/generated
    python3 scripts/prd_to_spec.py \
        --input specs/claims-auto-approval.json \
        --output specs/generated/
    
    if [ -f "specs/generated/specification.json" ]; then
        echo -e "${GREEN}✅ Specification generated${NC}"
        echo "   → specs/generated/specification.json"
    else
        echo -e "${RED}❌ Specification generation failed${NC}"
        exit 1
    fi
}

# Test Stage 2: Specification → Code
test_code_generation() {
    echo -e "\n${YELLOW}4. Testing Specification → Code${NC}"
    
    mkdir -p src/Generated tests/Generated
    python3 scripts/spec_to_code.py \
        --spec specs/generated/specification.json \
        --output src/Generated/
    
    if [ -f "src/Generated/ClaimsController.cs" ]; then
        echo -e "${GREEN}✅ Code generated${NC}"
        echo "   → src/Generated/ClaimsController.cs"
    else
        echo -e "${RED}❌ Code generation failed${NC}"
        exit 1
    fi
}

# Test Stage 3: Test Generation
test_test_generation() {
    echo -e "\n${YELLOW}5. Testing Test Generation${NC}"
    
    python3 scripts/generate_tests.py \
        --spec specs/generated/specification.json \
        --code src/Generated/ \
        --output tests/Generated/
    
    if [ -f "tests/Generated/ClaimsControllerTests.cs" ]; then
        echo -e "${GREEN}✅ Tests generated${NC}"
        echo "   → tests/Generated/ClaimsControllerTests.cs"
    else
        echo -e "${RED}❌ Test generation failed${NC}"
        exit 1
    fi
}

# Test Stage 4: AI Code Review
test_code_review() {
    echo -e "\n${YELLOW}6. Testing AI Code Review${NC}"
    
    python3 scripts/ai_code_review.py \
        --code src/Generated/ \
        --checklist "security,compliance,quality" \
        --output review-report.json
    
    if [ -f "review-report.json" ]; then
        SECURITY=$(python3 -c "import json; print(json.load(open('review-report.json')).get('security_score', 0))")
        echo -e "${GREEN}✅ Code review complete${NC}"
        echo "   → Security Score: $SECURITY/100"
    else
        echo -e "${RED}❌ Code review failed${NC}"
        exit 1
    fi
}

# Test Stage 5: Prompt Regression (Mock)
test_prompt_regression() {
    echo -e "\n${YELLOW}7. Testing Prompt Regression${NC}"
    
    # Create mock golden tests if none exist
    mkdir -p tests/golden
    if [ ! -f "tests/golden/claims_golden.json" ]; then
        cat > tests/golden/claims_golden.json << 'EOF'
[
  {
    "name": "approve_low_risk_claim",
    "input": {"claim_amount_gbp": 150, "damage_type": "SCREEN", "risk_score": 0.2},
    "expected_output": {"status": "APPROVED", "reason_code": "AUTO_250_LOW_RISK"}
  },
  {
    "name": "reject_high_amount",
    "input": {"claim_amount_gbp": 300, "damage_type": "SCREEN", "risk_score": 0.2},
    "expected_output": {"status": "MANUAL_REVIEW", "reason_code": "THRESHOLD_EXCEEDED"}
  }
]
EOF
    fi
    
    python3 scripts/prompt_regression.py \
        --golden-tests tests/golden/ \
        --threshold 0.90 \
        --output regression-report.json
    
    echo -e "${GREEN}✅ Prompt regression test complete${NC}"
}

# Summary
print_summary() {
    echo -e "\n${GREEN}=========================================="
    echo "✅ All Local Tests Passed!"
    echo "==========================================${NC}"
    echo ""
    echo "Generated Files:"
    echo "  📋 specs/generated/specification.json"
    echo "  💻 src/Generated/ClaimsController.cs"
    echo "  🧪 tests/Generated/ClaimsControllerTests.cs"
    echo "  📊 review-report.json"
    echo "  📈 regression-report.json"
    echo ""
    echo "Next Steps:"
    echo "  1. Review generated code: cat src/Generated/ClaimsController.cs"
    echo "  2. Push to trigger CI/CD: git add . && git commit -m 'test' && git push"
    echo "  3. Run with Act (local GitHub Actions): act -j spec-generation"
}

# Main
main() {
    check_prereqs
    install_deps
    test_spec_generation
    test_code_generation
    test_test_generation
    test_code_review
    test_prompt_regression
    print_summary
}

main "$@"
