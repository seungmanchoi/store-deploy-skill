#!/usr/bin/env python3
"""
Credential Manager for Store Deploy Plugin
- Saves/loads credentials to ~/.store-deploy/credentials.json
- First run: prompts interactively, then saves
- Subsequent runs: loads saved credentials
- Can merge project-level overrides from ./store-deploy.json
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

GLOBAL_DIR = Path.home() / ".store-deploy"
GLOBAL_CREDS_FILE = GLOBAL_DIR / "credentials.json"
PROJECT_CREDS_FILE = "store-deploy.json"

DEFAULT_CREDENTIALS = {
    "account": {
        "apple_id": "",
        "team_id": "",
        "itc_team_id": "",
        "asc_key_id": "",
        "asc_issuer_id": "",
        "asc_key_path": "",
        "google_service_account_path": "",
        "google_service_account_email": "",
    },
    "contact": {
        "first_name": "",
        "last_name": "",
        "email": "",
        "phone": "",
    },
    "defaults": {
        "has_ads": False,
        "has_ugc": False,
        "has_encryption": False,
        "has_iap": False,
        "min_age": 18,
        "privacy_url": "",
        "ad_types": ["banner", "interstitial", "rewarded"],
    },
}

# Interactive prompts for each field
PROMPTS = {
    "account.apple_id": "Apple ID (email)",
    "account.team_id": "Apple Team ID",
    "account.itc_team_id": "App Store Connect Team ID (ITC)",
    "account.asc_key_id": "App Store Connect API Key ID",
    "account.asc_issuer_id": "App Store Connect Issuer ID",
    "account.asc_key_path": "App Store Connect API Key file path (.p8)",
    "account.google_service_account_path": "Google Play service account JSON path",
    "account.google_service_account_email": "Google Play service account email",
    "contact.first_name": "Contact first name",
    "contact.last_name": "Contact last name",
    "contact.email": "Contact email",
    "contact.phone": "Contact phone (optional, press Enter to skip)",
}


def _deep_get(d: dict, dotted_key: str) -> Any:
    keys = dotted_key.split(".")
    for k in keys:
        d = d.get(k, {})
    return d


def _deep_set(d: dict, dotted_key: str, value: Any):
    keys = dotted_key.split(".")
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = value


def load_global() -> dict:
    """Load global credentials from ~/.store-deploy/credentials.json"""
    if GLOBAL_CREDS_FILE.exists():
        with open(GLOBAL_CREDS_FILE) as f:
            saved = json.load(f)
        # Merge with defaults to fill any new fields
        merged = json.loads(json.dumps(DEFAULT_CREDENTIALS))
        _recursive_merge(merged, saved)
        return merged
    return json.loads(json.dumps(DEFAULT_CREDENTIALS))


def save_global(creds: dict):
    """Save credentials to ~/.store-deploy/credentials.json"""
    GLOBAL_DIR.mkdir(parents=True, exist_ok=True)
    with open(GLOBAL_CREDS_FILE, "w") as f:
        json.dump(creds, f, indent=2, ensure_ascii=False)
    # Restrict permissions
    os.chmod(GLOBAL_CREDS_FILE, 0o600)
    print(f"[✓] Credentials saved to {GLOBAL_CREDS_FILE}")


def load_project(project_root: str = ".") -> dict:
    """Load project-level overrides from ./store-deploy.json"""
    p = Path(project_root) / PROJECT_CREDS_FILE
    if p.exists():
        with open(p) as f:
            return json.load(f)
    return {}


def save_project(data: dict, project_root: str = "."):
    """Save project-level config to ./store-deploy.json"""
    p = Path(project_root) / PROJECT_CREDS_FILE
    with open(p, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[✓] Project config saved to {p}")


def load_merged(project_root: str = ".") -> dict:
    """Load global credentials merged with project-level overrides."""
    creds = load_global()
    project = load_project(project_root)
    _recursive_merge(creds, project)
    return creds


def _recursive_merge(base: dict, override: dict):
    """Recursively merge override into base (mutates base)."""
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            _recursive_merge(base[k], v)
        else:
            base[k] = v


def is_configured(creds: dict) -> bool:
    """Check if minimum required credentials are set."""
    account = creds.get("account", {})
    contact = creds.get("contact", {})
    return bool(account.get("apple_id") and contact.get("email"))


def interactive_setup(existing: Optional[dict] = None) -> dict:
    """Interactively prompt for credentials. Shows existing values as defaults."""
    if existing is None:
        existing = load_global()

    print("\n" + "=" * 50)
    print("  Store Deploy — Credential Setup")
    print("=" * 50)
    print("Enter credentials (press Enter to keep current value)\n")

    creds = json.loads(json.dumps(existing))

    for dotted_key, prompt_text in PROMPTS.items():
        current = _deep_get(existing, dotted_key)
        display = current if current else "(not set)"

        if dotted_key.endswith("_path") and current:
            # Show just filename for paths
            display = Path(current).name if current else "(not set)"

        user_input = input(f"  {prompt_text} [{display}]: ").strip()
        if user_input:
            _deep_set(creds, dotted_key, user_input)

    save_global(creds)
    return creds


def ensure_credentials(project_root: str = ".", force_setup: bool = False) -> dict:
    """
    Ensure credentials are available.
    - If saved and valid: return them
    - If missing or force_setup: run interactive setup
    """
    creds = load_merged(project_root)

    if force_setup or not is_configured(creds):
        if not sys.stdin.isatty():
            print("[!] No saved credentials and not running interactively.")
            print(f"    Run: python3 {__file__} --setup")
            sys.exit(1)
        creds = interactive_setup(creds)
        creds = load_merged(project_root)  # Re-merge with project

    return creds


def print_credentials(creds: dict):
    """Print credentials summary (masking sensitive values)."""
    print("\n  Current Credentials:")
    print("  " + "-" * 40)

    account = creds.get("account", {})
    contact = creds.get("contact", {})

    print(f"  Apple ID:        {account.get('apple_id', '(not set)')}")
    print(f"  Team ID:         {account.get('team_id', '(not set)')}")
    print(f"  ITC Team ID:     {account.get('itc_team_id', '(not set)')}")
    print(f"  ASC Key ID:      {account.get('asc_key_id', '(not set)')}")
    print(f"  ASC Issuer ID:   {_mask(account.get('asc_issuer_id', ''))}")
    print(f"  ASC Key Path:    {account.get('asc_key_path', '(not set)')}")
    print(f"  Google SA Path:  {account.get('google_service_account_path', '(not set)')}")
    print(f"  Google SA Email: {account.get('google_service_account_email', '(not set)')}")
    print(f"  Contact:         {contact.get('first_name', '')} {contact.get('last_name', '')}")
    print(f"  Contact Email:   {contact.get('email', '(not set)')}")
    print()


def _mask(value: str) -> str:
    if not value or len(value) < 8:
        return value or "(not set)"
    return value[:4] + "****" + value[-4:]


# --- CLI ---
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Store Deploy Credential Manager")
    parser.add_argument("--setup", action="store_true", help="Run interactive setup")
    parser.add_argument("--show", action="store_true", help="Show current credentials")
    parser.add_argument("--project", default=".", help="Project root directory")
    parser.add_argument("--json", action="store_true", help="Output as JSON (for scripts)")
    parser.add_argument("--get", type=str, help="Get a specific key (dotted notation)")
    args = parser.parse_args()

    if args.setup:
        interactive_setup()
    elif args.show:
        creds = load_merged(args.project)
        print_credentials(creds)
    elif args.json:
        creds = load_merged(args.project)
        print(json.dumps(creds, indent=2, ensure_ascii=False))
    elif args.get:
        creds = load_merged(args.project)
        val = _deep_get(creds, args.get)
        print(val if val else "")
    else:
        # Default: ensure credentials exist, show summary
        creds = ensure_credentials(args.project)
        print_credentials(creds)


if __name__ == "__main__":
    main()
