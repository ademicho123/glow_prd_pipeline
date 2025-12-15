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
    required_fields = ['endpoints', 'models', 'metadata']
    for field in required_fields:
        if field not in spec_data:
            errors.append(f"Missing required field: {field}")

    # Validate endpoints
    if 'endpoints' in spec_data:
        endpoints = spec_data['endpoints']
        if not isinstance(endpoints, list):
            errors.append("'endpoints' must be a list")
        else:
            for idx, endpoint in enumerate(endpoints):
                if not isinstance(endpoint, dict):
                    errors.append(f"Endpoint {idx} must be a dictionary")
                    continue

                # Check required endpoint fields
                required_endpoint_fields = ['path', 'method', 'handler']
                for field in required_endpoint_fields:
                    if field not in endpoint:
                        errors.append(f"Endpoint {idx}: Missing required field '{field}'")

    # Validate models
    if 'models' in spec_data:
        models = spec_data['models']
        if not isinstance(models, list):
            errors.append("'models' must be a list")
        else:
            for idx, model in enumerate(models):
                if not isinstance(model, dict):
                    errors.append(f"Model {idx} must be a dictionary")
                    continue

                # Check required model fields
                if 'name' not in model:
                    errors.append(f"Model {idx}: Missing required field 'name'")
                if 'properties' not in model:
                    errors.append(f"Model {idx}: Missing required field 'properties'")

    # Validate metadata
    if 'metadata' in spec_data:
        metadata = spec_data['metadata']
        if not isinstance(metadata, dict):
            errors.append("'metadata' must be a dictionary")

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
        num_endpoints = len(spec_data.get('endpoints', []))
        num_models = len(spec_data.get('models', []))
        print(f"\nSpecification summary:")
        print(f"  - Endpoints: {num_endpoints}")
        print(f"  - Models: {num_models}")

        sys.exit(0)


if __name__ == '__main__':
    main()
