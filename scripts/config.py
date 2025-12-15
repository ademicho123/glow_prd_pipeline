#!/usr/bin/env python3
r"""
Glow AI-Native Pipeline - Configuration Loader

Loads environment variables from .env file in PARENT directory.
This keeps secrets outside the project folder (safe from AI tools).

Expected structure:
    C:\Users\ELITEBOOK\OneDrive\Desktop\Projects\.env        ← secrets here
    C:\Users\ELITEBOOK\OneDrive\Desktop\Projects\glow_prd\   ← project here

.env location priority:
1. GLOW_ENV_PATH environment variable (if set)
2. Parent directory of project (../.env)
3. Two levels up (../../.env)
"""

import os
from pathlib import Path

def load_config():
    """Load configuration from .env file in parent directory."""
    
    env_path = None
    
    # Priority 1: Explicit path via environment variable
    if os.environ.get('GLOW_ENV_PATH'):
        env_path = os.environ.get('GLOW_ENV_PATH')
    
    # Priority 2: Parent directory (Projects/.env when running from Projects/glow_prd/)
    if not env_path:
        # Get the project root (where scripts folder is)
        project_root = Path(__file__).parent.parent
        
        # Look for .env in parent of project root
        parent_env = project_root.parent / ".env"
        
        if parent_env.exists():
            env_path = str(parent_env)
    
    # Priority 3: Two levels up (in case of nested structure)
    if not env_path:
        project_root = Path(__file__).parent.parent
        grandparent_env = project_root.parent.parent / ".env"
        
        if grandparent_env.exists():
            env_path = str(grandparent_env)
    
    # Load .env file
    if env_path and Path(env_path).exists():
        print(f"📁 Loading config from: {env_path}")
        _load_env_file(env_path)
    else:
        print("⚠️  No .env file found in parent directory.")
        print("   Expected: ../. env (relative to project root)")
        print("   Or set: GLOW_ENV_PATH environment variable")
    
    # Validate required keys
    _validate_config()
    
    return get_config()

def _load_env_file(filepath: str):
    """Parse and load .env file into environment."""
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value

def _validate_config():
    """Validate required configuration is present."""
    required = ['OPENAI_API_KEY']
    missing = [key for key in required if not os.environ.get(key)]
    
    if missing:
        print(f"❌ Missing required config: {', '.join(missing)}")
        print(f"   Add to .env file in parent directory")
        raise EnvironmentError(f"Missing configuration: {missing}")
    
    print("✅ Configuration loaded successfully")

def get_config() -> dict:
    """Get all configuration as dictionary."""
    return {
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
        'AZURE_CLIENT_ID': os.environ.get('AZURE_CLIENT_ID'),
        'AZURE_CLIENT_SECRET': os.environ.get('AZURE_CLIENT_SECRET'),
        'AZURE_TENANT_ID': os.environ.get('AZURE_TENANT_ID'),
        'AZURE_SUBSCRIPTION_ID': os.environ.get('AZURE_SUBSCRIPTION_ID'),
    }

# Auto-load on import
if __name__ != "__main__":
    load_config()
