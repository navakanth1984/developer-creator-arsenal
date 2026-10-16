"""
Grok Plugin Packaging & Verification Script
Validates plugin.json manifest, checks MCP schema compliance, and prepares the distribution bundle for xAI submission.
"""

import json
import os
import subprocess
import sys

def validate_manifest(manifest_path: str) -> bool:
    print(f"[+] Validating manifest: {manifest_path}")
    if not os.path.exists(manifest_path):
        print("[-] Error: plugin.json not found!")
        return False

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    required_keys = ["name", "version", "displayName", "description", "entrypoint", "protocol", "tools"]
    for key in required_keys:
        if key not in data:
            print(f"[-] Missing required manifest key: {key}")
            return False

    if data.get("protocol") != "mcp":
        print("[-] Error: protocol must be 'mcp'")
        return False

    if not isinstance(data.get("tools"), list) or len(data["tools"]) == 0:
        print("[-] Error: 'tools' must be a non-empty array.")
        return False

    print(f"[✓] Manifest valid! Plugin: {data['displayName']} (v{data['version']}) with {len(data['tools'])} tools.")
    return True

def run_mcp_test(entrypoint_path: str) -> bool:
    print(f"[+] Verifying MCP server entrypoint: {entrypoint_path}")
    res = subprocess.run([sys.executable, entrypoint_path, "--test"], capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[-] MCP self-test failed with code {res.returncode}:\n{res.stderr}")
        return False

    if "enterprise-code-security-auditor" in res.stdout and "tools/list" in res.stdout:
        print("[✓] MCP Server self-test passed successfully!")
        return True
    else:
        print("[-] Unexpected MCP response output.")
        return False

def main():
    base_dir = os.path.dirname(__file__)
    manifest = os.path.join(base_dir, "plugin.json")
    entrypoint = os.path.join(base_dir, "mcp_server.py")

    if not validate_manifest(manifest):
        sys.exit(1)

    if not run_mcp_test(entrypoint):
        sys.exit(1)

    bundle_meta = {
        "status": "ready_for_xai_marketplace_submission",
        "portal": "https://x.ai/bot/marketplace/submit-a-plugin",
        "cli_install_command": "grok plugin install ./02-grok-plugin-connector"
    }

    out_file = os.path.join(base_dir, "submission_bundle.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(bundle_meta, f, indent=2)

    print(f"[✓] Packaging complete! Verification report saved to: {out_file}")

if __name__ == "__main__":
    main()
