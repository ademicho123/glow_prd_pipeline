# Glow AI-Native Pipeline - Makefile
# Usage: make <target>

.PHONY: help install test test-spec test-code test-review test-all docker clean

# Default target
help:
	@echo "Glow AI-Native Pipeline - Test Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install     Install Python dependencies"
	@echo "  make setup       Full setup (install + create dirs)"
	@echo ""
	@echo "Test Individual Stages:"
	@echo "  make test-spec   Test PRD → Specification"
	@echo "  make test-code   Test Specification → Code"
	@echo "  make test-tests  Test Test Generation"
	@echo "  make test-review Test AI Code Review"
	@echo "  make test-regression Test Prompt Regression"
	@echo ""
	@echo "Full Tests:"
	@echo "  make test        Run all stages sequentially"
	@echo "  make test-docker Run via Docker Compose"
	@echo "  make test-act    Run GitHub Actions locally (requires act)"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean       Remove generated files"
	@echo "  make view-spec   View generated specification"
	@echo "  make view-code   View generated code"

# ============================================================
# SETUP
# ============================================================
install:
	pip install -r requirements.txt

setup: install
	mkdir -p specs/generated src/Generated tests/Generated tests/golden output

# ============================================================
# INDIVIDUAL STAGE TESTS
# ============================================================
test-spec:
	@echo "📋 Testing PRD → Specification..."
	python scripts/prd_to_spec.py \
		--input specs/claims-auto-approval.json \
		--output specs/generated/
	@echo "✅ Done: specs/generated/specification.json"

test-code: test-spec
	@echo "⚡ Testing Specification → Code..."
	python scripts/spec_to_code.py \
		--spec specs/generated/specification.json \
		--output src/Generated/
	@echo "✅ Done: src/Generated/"

test-tests: test-code
	@echo "🧪 Testing Test Generation..."
	python scripts/generate_tests.py \
		--spec specs/generated/specification.json \
		--code src/Generated/ \
		--output tests/Generated/
	@echo "✅ Done: tests/Generated/"

test-review: test-code
	@echo "🤖 Testing AI Code Review..."
	python scripts/ai_code_review.py \
		--code src/Generated/ \
		--checklist "security,compliance,quality" \
		--output review-report.json
	@echo "✅ Done: review-report.json"
	@cat review-report.json | python -c "import sys,json; r=json.load(sys.stdin); print(f'Security: {r.get(\"security_score\",0)}/100')"

test-regression:
	@echo "📈 Testing Prompt Regression..."
	@mkdir -p tests/golden
	@if [ ! -f tests/golden/claims_golden.json ]; then \
		echo '[{"name":"test","input":{"claim_amount_gbp":150,"damage_type":"SCREEN","risk_score":0.2},"expected_output":{"status":"APPROVED","reason_code":"AUTO_250_LOW_RISK"}}]' > tests/golden/claims_golden.json; \
	fi
	python scripts/prompt_regression.py \
		--golden-tests tests/golden/ \
		--threshold 0.90 \
		--output regression-report.json
	@echo "✅ Done: regression-report.json"

# ============================================================
# FULL TESTS
# ============================================================
test: setup test-spec test-code test-tests test-review
	@echo ""
	@echo "=========================================="
	@echo "✅ All Pipeline Stages Passed!"
	@echo "=========================================="

test-docker:
	@echo "🐳 Running via Docker Compose..."
	docker-compose up --build pipeline
	@echo "✅ Check ./output folder for results"

test-act:
	@echo "🎬 Running GitHub Actions locally..."
	@command -v act >/dev/null 2>&1 || { echo "Install act: brew install act"; exit 1; }
	act -j spec-generation --secret OPENAI_API_KEY=$(OPENAI_API_KEY)

# ============================================================
# UTILITIES
# ============================================================
clean:
	rm -rf specs/generated/* src/Generated/* tests/Generated/*
	rm -f review-report.json regression-report.json
	rm -rf output/*
	@echo "🧹 Cleaned generated files"

view-spec:
	@cat specs/generated/specification.json | python -m json.tool

view-code:
	@cat src/Generated/ClaimsController.cs

view-review:
	@cat review-report.json | python -m json.tool

# Quick check if OPENAI_API_KEY is set
check-env:
	@if [ -z "$(OPENAI_API_KEY)" ]; then \
		echo "❌ OPENAI_API_KEY not set"; \
		echo "Run: export OPENAI_API_KEY='sk-...'"; \
		exit 1; \
	else \
		echo "✅ OPENAI_API_KEY is set"; \
	fi
