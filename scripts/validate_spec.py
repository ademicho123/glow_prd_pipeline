#!/usr/bin/env python3
"""
Validate the generated specification JSON schema.
Ensures the specification file is well-formed and contains required fields.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List


def validate_specification(spec_data: Dict[str, Any]) -> List[str]:
    """
    Validate the specification schema.

    Args:
        spec_data: The parsed specification JSON

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Check required top-level fields
    required_fields = ['api_contract', 'inputs', 'outputs', 'decision_rules']
    for field in required_fields:
        if field not in spec_data:
            errors.append(f"Missing required field: {field}")

    # Validate api_contract
    if 'api_contract' in spec_data:
        api_contract = spec_data['api_contract']
        if not isinstance(api_contract, dict):
            errors.append("'api_contract' must be a dictionary")
        else:
            required_contract_fields = ['method', 'endpoint']
            for field in required_contract_fields:
                if field not in api_contract:
                    errors.append(f"api_contract: Missing required field '{field}'")

    # Validate inputs
    if 'inputs' in spec_data:
        inputs = spec_data['inputs']
        if not isinstance(inputs, list):
            errors.append("'inputs' must be a list")
        else:
            for idx, input_field in enumerate(inputs):
                if not isinstance(input_field, dict):
                    errors.append(f"Input {idx} must be a dictionary")
                    continue

                # Check required input fields
                required_input_fields = ['name', 'type', 'required']
                for field in required_input_fields:
                    if field not in input_field:
                        errors.append(f"Input {idx}: Missing required field '{field}'")

    # Validate outputs
    if 'outputs' in spec_data:
        outputs = spec_data['outputs']
        if not isinstance(outputs, dict):
            errors.append("'outputs' must be a dictionary")
        else:
            if 'success' not in outputs:
                errors.append("outputs: Missing required field 'success'")
            if 'error' not in outputs:
                errors.append("outputs: Missing required field 'error'")

    # Validate decision_rules
    if 'decision_rules' in spec_data:
        decision_rules = spec_data['decision_rules']
        if not isinstance(decision_rules, list):
            errors.append("'decision_rules' must be a list")
        else:
            for idx, rule in enumerate(decision_rules):
                if not isinstance(rule, dict):
                    errors.append(f"Decision rule {idx} must be a dictionary")
                    continue

                # Check required rule fields
                required_rule_fields = ['condition', 'action']
                for field in required_rule_fields:
                    if field not in rule:
                        errors.append(f"Decision rule {idx}: Missing required field '{field}'")

    # Validate compliance (optional but should be structured correctly if present)
    if 'compliance' in spec_data:
        compliance = spec_data['compliance']
        if not isinstance(compliance, dict):
            errors.append("'compliance' must be a dictionary")

    # Validate constraints (optional but should be structured correctly if present)
    if 'constraints' in spec_data:
        constraints = spec_data['constraints']
        if not isinstance(constraints, dict):
            errors.append("'constraints' must be a dictionary")

    return errors


def main():
    """Main validation function."""
    if len(sys.argv) < 2:
        print("Usage: python validate_spec.py <spec_file.json>")
        sys.exit(1)

    spec_file = Path(sys.argv[1])

    # Check if file exists
    if not spec_file.exists():
        print(f"❌ Error: Specification file not found: {spec_file}")
        sys.exit(1)

    # Parse JSON
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            spec_data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON in {spec_file}")
        print(f"   {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file {spec_file}: {e}")
        sys.exit(1)

    # Validate specification
    errors = validate_specification(spec_data)

    if errors:
        print(f"❌ Validation failed for {spec_file}")
        print(f"\nFound {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print(f"✅ Validation passed for {spec_file}")

        # Print summary
        num_inputs = len(spec_data.get('inputs', []))
        num_rules = len(spec_data.get('decision_rules', []))
        api_endpoint = spec_data.get('api_contract', {}).get('endpoint', 'N/A')
        api_method = spec_data.get('api_contract', {}).get('method', 'N/A')

        print(f"\nSpecification summary:")
        print(f"  - API Endpoint: {api_method} {api_endpoint}")
        print(f"  - Input Fields: {num_inputs}")
        print(f"  - Decision Rules: {num_rules}")

        sys.exit(0)


if __name__ == '__main__':
    main()
