#!/usr/bin/env python3
"""
AI Code Review
Performs security, quality, and compliance review on generated code.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, UTC

# Load config first (handles .env loading)
import config

from openai import OpenAI

client = OpenAI()  # Uses OPENAI_API_KEY from environment

REVIEW_PROMPT = """You are a senior security engineer and code reviewer at Glow Financial Services.
Review the provided code for security vulnerabilities, quality issues, and compliance requirements.

CHECKLIST:
1. SECURITY
   - SQL injection vulnerabilities
   - Hardcoded secrets/credentials
   - Input validation gaps
   - Authentication/authorization issues
   - Insecure data handling
   - OWASP Top 10 vulnerabilities

2. COMPLIANCE
   - FCA regulatory requirements
   - GDPR data handling
   - PII logging violations
   - Audit trail completeness
   - Decision traceability

3. QUALITY
   - Error handling completeness
   - Null reference risks
   - Resource leaks
   - Performance concerns
   - Code maintainability

4. BEST PRACTICES
   - SOLID principles adherence
   - Proper async/await usage
   - Exception handling patterns
   - Logging practices

OUTPUT JSON:
{
  "security_score": 0-100,
  "quality_score": 0-100,
  "compliance_score": 0-100,
  "critical_issues": [{"type": "...", "location": "...", "description": "...", "severity": "critical"}],
  "warnings": [{"type": "...", "location": "...", "description": "...", "severity": "warning"}],
  "suggestions": ["..."],
  "passed": true/false
}"""

def load_code_files(directory: str) -> dict:
    """Load all Python files from directory."""
    code_dir = Path(directory)
    files = {}
    for py_file in code_dir.glob("**/*.py"):
        with open(py_file, 'r') as f:
            files[str(py_file)] = f.read()
    return files

def review_code(files: dict, checklist: list) -> dict:
    """Perform AI code review."""

    code_content = ""
    for filepath, content in files.items():
        code_content += f"\n# === FILE: {filepath} ===\n{content}\n"
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": REVIEW_PROMPT},
            {"role": "user", "content": f"""Review this code focusing on: {', '.join(checklist)}

{code_content}

Provide detailed review in JSON format."""}
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )
    
    review = json.loads(response.choices[0].message.content)
    
    # Add metadata
    review["_metadata"] = {
        "reviewed_at": datetime.now(UTC).isoformat(),
        "files_reviewed": list(files.keys()),
        "checklist": checklist
    }
    
    # Determine pass/fail
    review["passed"] = (
        len(review.get("critical_issues", [])) == 0 and
        review.get("security_score", 0) >= 80 and
        review.get("compliance_score", 0) >= 90
    )
    
    return review

def main():
    parser = argparse.ArgumentParser(description="AI Code Review")
    parser.add_argument("--code", required=True, help="Code directory to review")
    parser.add_argument("--checklist", default="security,quality,compliance,best-practices",
                        help="Comma-separated review checklist")
    parser.add_argument("--output", required=True, help="Output report file")
    args = parser.parse_args()
    
    print(f"📂 Loading code from: {args.code}")
    files = load_code_files(args.code)
    print(f"   Found {len(files)} files")
    
    checklist = args.checklist.split(",")
    print(f"🔍 Running AI review: {', '.join(checklist)}")
    
    review = review_code(files, checklist)
    
    # Save report
    with open(args.output, 'w') as f:
        json.dump(review, f, indent=2)
    
    # Print summary
    print(f"\n📊 Review Results:")
    print(f"   Security Score:   {review.get('security_score', 'N/A')}/100")
    print(f"   Quality Score:    {review.get('quality_score', 'N/A')}/100")
    print(f"   Compliance Score: {review.get('compliance_score', 'N/A')}/100")
    print(f"   Critical Issues:  {len(review.get('critical_issues', []))}")
    print(f"   Warnings:         {len(review.get('warnings', []))}")
    
    if review.get("passed"):
        print(f"\n✅ Code review PASSED")
    else:
        print(f"\n❌ Code review FAILED")
        if review.get("critical_issues"):
            print("\nCritical Issues:")
            for issue in review["critical_issues"]:
                print(f"   - [{issue.get('type')}] {issue.get('description')}")
    
    print(f"\n💾 Full report: {args.output}")

if __name__ == "__main__":
    main()
