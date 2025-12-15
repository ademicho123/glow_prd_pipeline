#!/usr/bin/env python3
"""
Prompt Regression Testing
Detects logic drift by comparing current LLM outputs against golden test cases.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, UTC

# Load config first (handles .env loading)
import config

from openai import OpenAI

client = OpenAI()  # Uses OPENAI_API_KEY from environment

def load_golden_tests(directory: str) -> list:
    """Load all golden test cases."""
    golden_dir = Path(directory)
    tests = []
    
    for json_file in golden_dir.glob("*.json"):
        with open(json_file, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                tests.extend(data)
            else:
                tests.append(data)
    
    return tests

def run_test(test_case: dict) -> dict:
    """Run a single golden test case against current model."""
    
    # Reconstruct the prompt that would generate this decision
    prompt = f"""Given this claims request:
{json.dumps(test_case['input'], indent=2)}

Apply the decision rules and return:
{{"status": "APPROVED" or "MANUAL_REVIEW", "reason_code": "..."}}"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are the Glow Claims decision engine. Apply business rules exactly."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0
    )
    
    actual = json.loads(response.choices[0].message.content)
    expected = test_case.get("expected_output", {})
    
    return {
        "name": test_case.get("name", "unnamed"),
        "input": test_case["input"],
        "expected": expected,
        "actual": actual,
        "passed": (
            actual.get("status") == expected.get("status") and
            actual.get("reason_code") == expected.get("reason_code")
        )
    }

def calculate_similarity(expected: dict, actual: dict) -> float:
    """Calculate similarity score between expected and actual outputs."""
    if expected == actual:
        return 1.0
    
    matches = 0
    total = len(expected)
    
    for key, value in expected.items():
        if actual.get(key) == value:
            matches += 1
    
    return matches / total if total > 0 else 0.0

def main():
    parser = argparse.ArgumentParser(description="Prompt Regression Testing")
    parser.add_argument("--golden-tests", required=True, help="Directory with golden test cases")
    parser.add_argument("--threshold", type=float, default=0.95, help="Pass threshold (0-1)")
    parser.add_argument("--output", required=True, help="Output report file")
    args = parser.parse_args()
    
    print(f"📋 Loading golden tests from: {args.golden_tests}")
    golden_tests = load_golden_tests(args.golden_tests)
    print(f"   Found {len(golden_tests)} test cases")
    
    print(f"🧪 Running regression tests...")
    
    results = []
    passed = 0
    failed = 0
    
    for test in golden_tests:
        result = run_test(test)
        results.append(result)
        
        if result["passed"]:
            passed += 1
            print(f"   ✅ {result['name']}")
        else:
            failed += 1
            print(f"   ❌ {result['name']}")
            print(f"      Expected: {result['expected']}")
            print(f"      Actual:   {result['actual']}")
    
    # Calculate metrics
    pass_rate = passed / len(golden_tests) if golden_tests else 0
    drift_detected = pass_rate < args.threshold
    
    report = {
        "timestamp": datetime.now(UTC).isoformat(),
        "total_tests": len(golden_tests),
        "passed": passed,
        "failed": failed,
        "pass_rate": pass_rate,
        "threshold": args.threshold,
        "drift_detected": drift_detected,
        "drift_details": [r for r in results if not r["passed"]],
        "results": results
    }
    
    # Save report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Summary
    print(f"\n📊 Regression Test Results:")
    print(f"   Total:     {len(golden_tests)}")
    print(f"   Passed:    {passed}")
    print(f"   Failed:    {failed}")
    print(f"   Pass Rate: {pass_rate:.1%}")
    print(f"   Threshold: {args.threshold:.1%}")
    
    if drift_detected:
        print(f"\n⚠️  DRIFT DETECTED - Pass rate below threshold")
        exit(1)
    else:
        print(f"\n✅ No drift detected")
    
    print(f"\n💾 Report saved: {args.output}")

if __name__ == "__main__":
    main()
