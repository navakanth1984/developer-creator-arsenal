"""
Shift-Left Test Suite: Autonomous Developer-Creator Arsenal
Validates all 6 engines in < 5 seconds under Karpathy Coding Guidelines and ACDLC Stage 5.
"""

import subprocess
import sys
import time
import os

TEST_CASES = [
    {
        "name": "Engine 01: REA Clean-Room Harness",
        "cmd": [sys.executable, "rea_runner.py"],
        "cwd": "01-reverse-engineer-anything",
        "expected": "Extracted 5 endpoint contracts"
    },
    {
        "name": "Engine 02: Grok MCP Plugin Server",
        "cmd": [sys.executable, "mcp_server.py", "--test"],
        "cwd": "02-grok-plugin-connector",
        "expected": "enterprise-code-security-auditor"
    },
    {
        "name": "Engine 02: Grok Plugin Packager",
        "cmd": [sys.executable, "package_plugin.py"],
        "cwd": "02-grok-plugin-connector",
        "expected": "Packaging complete!"
    },
    {
        "name": "Engine 03: Hypit SVML Compiler",
        "cmd": [sys.executable, "svml_compiler.py"],
        "cwd": "03-hypit-svml-video-engine",
        "expected": "Compiled SVML with 18 words"
    },
    {
        "name": "Engine 04: Agent Use Cases Curator",
        "cmd": [sys.executable, "curator.py"],
        "cwd": "04-agent-usecases-hub",
        "expected": "Curated 3 verified agent use cases"
    },
    {
        "name": "Engine 06: Catalyst Advanced I/O Function",
        "cmd": [sys.executable, "main.py"],
        "cwd": "06-higgsfield-catalyst-replica/functions/higgsfield_api",
        "expected": "Wan 2.1 Cinema SOTA"
    },
    {
        "name": "Engine 06: Catalyst GPU Worker Loop",
        "cmd": [sys.executable, "gpu_worker_pull.py"],
        "cwd": "06-higgsfield-catalyst-replica/worker",
        "expected": "Render complete!"
    }
]

def run_tests():
    print("=" * 65)
    print("🚀 SHIFT-LEFT REASONING & INTEGRITY TEST SUITE (ACDLC STAGE 5)")
    print("=" * 65)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    start_time = time.time()
    passed = 0
    failed = 0

    for tc in TEST_CASES:
        work_dir = os.path.join(base_dir, tc["cwd"])
        print(f"\n[RUNNING] {tc['name']}...")
        t0 = time.time()
        try:
            res = subprocess.run(tc["cmd"], cwd=work_dir, capture_output=True, text=True, timeout=10)
            elapsed = time.time() - t0
            output = res.stdout + res.stderr
            if res.returncode == 0 and tc["expected"] in output:
                print(f"  [✓ PASS] ({elapsed:.2f}s)")
                passed += 1
            else:
                print(f"  [✗ FAIL] ({elapsed:.2f}s) Return code: {res.returncode}")
                print(f"  Output:\n{output[:300]}")
                failed += 1
        except Exception as e:
            print(f"  [✗ ERROR] Exception: {str(e)}")
            failed += 1

    total_elapsed = time.time() - start_time
    print("\n" + "=" * 65)
    print(f"📊 SUMMARY: {passed} PASSED, {failed} FAILED in {total_elapsed:.2f}s")
    if failed == 0 and total_elapsed < 5.0:
        print("🎯 SUB-MINUTE TEST GATE SATISFIED (<5s SLA). ALL GATES GREEN!")
    print("=" * 65)
    
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
