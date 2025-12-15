#!/usr/bin/env python3
"""
PRD → Structured Specification Generator
Converts business requirements into machine-readable specifications for code generation.
"""

import json
import argparse
import os
from pathlib import Path
from datetime import datetime, UTC

# Load config first (handles .env loading)
import config

from openai import OpenAI

client = OpenAI()  # Uses OPENAI_API_KEY from environment

SYSTEM_PROMPT = """You are a specification architect for Glow Financial Services.
Convert business requirements into structured JSON specifications.

Output MUST follow this exact schema:
{
  "api_contract": {
    "method": "POST|GET|PUT|DELETE",
    "endpoint": "/api/v1/...",
    "version": "1.0"
  },
  "inputs": [
    {"name": "field_name", "type": "string|number|boolean", "required": true, "validation": "..."}
  ],
  "outputs": {
    "success": {"status": "...", "fields": [...]},
    "error": {"codes": [...]}
  },
  "decision_rules": [
    {"condition": "IF ...", "action": "THEN ...", "reason_code": "..."}
  ],
  "compliance": {
    "regulations": ["FCA", "GDPR"],
    "audit_requirements": ["..."],
    "pii_fields": ["..."]
  },
  "constraints": {
    "max_values": {...},
    "allowed_enums": {...}
  }
}

Be precise. Be deterministic. Every rule must be auditable."""

def load_prd(filepath: str) -> dict:
    """Load PRD from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def generate_specification(prd: dict) -> dict:
    """Use LLM to generate structured specification from PRD."""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Convert this PRD to specification:\n\n{json.dumps(prd, indent=2)}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.1  # Low temperature for deterministic output
    )
    
    spec = json.loads(response.choices[0].message.content)
    
    # Add metadata
    spec["_metadata"] = {
        "generated_at": datetime.now(UTC).isoformat(),
        "source_prd": prd.get("id", "unknown"),
        "generator_version": "1.0.0",
        "model": "gpt-4o"
    }
    
    return spec

def validate_specification(spec: dict) -> bool:
    """Validate specification has required fields."""
    required = ["api_contract", "inputs", "outputs", "decision_rules", "compliance"]
    
    for field in required:
        if field not in spec:
            raise ValueError(f"Missing required field: {field}")
    
    if not spec["decision_rules"]:
        raise ValueError("Specification must have at least one decision rule")
    
    return True

def main():
    parser = argparse.ArgumentParser(description="Generate specification from PRD")
    parser.add_argument("--input", required=True, help="Input PRD file")
    parser.add_argument("--output", required=True, help="Output directory")
    args = parser.parse_args()
    
    # Load PRD
    print(f"📋 Loading PRD: {args.input}")
    prd = load_prd(args.input)
    
    # Generate specification
    print("⚡ Generating structured specification...")
    spec = generate_specification(prd)
    
    # Validate
    print("✅ Validating specification schema...")
    validate_specification(spec)
    
    # Save
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "specification.json"
    with open(output_file, 'w') as f:
        json.dump(spec, f, indent=2)
    
    print(f"💾 Specification saved: {output_file}")
    
    # Summary
    print(f"\n📊 Specification Summary:")
    print(f"   - API: {spec['api_contract']['method']} {spec['api_contract']['endpoint']}")
    print(f"   - Inputs: {len(spec['inputs'])} fields")
    print(f"   - Rules: {len(spec['decision_rules'])} decision rules")
    print(f"   - Compliance: {', '.join(spec['compliance']['regulations'])}")

if __name__ == "__main__":
    main()
