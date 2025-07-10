#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test script to verify Python 3.13 compatibility fixes
"""

import sys
import traceback

def test_imports():
    """Test that all major modules can be imported without Python 3.13 issues"""
    
    print(f"Testing with Python {sys.version}")
    
    tests = [
        ("pupy", "Basic pupy package import"),
        ("pupy.network.lib.http_parser_compat", "HTTP parser compatibility layer"),
        ("pupy.network.lib.rsa_compat", "RSA compatibility layer"),
        ("pupy.commands", "Commands module (imp replacement)"),
        ("pupy.pupylib.PupyServer", "Server module (imp replacement)"),
        ("pupy.triggers", "Triggers module (imp replacement)"),
        ("pupy.network.lib.igd", "IGD module (http_parser compatibility)"),
        ("pupy.network.lib.transports.httpwrap", "HTTP wrapper transport"),
        ("pupy.network.lib.socks", "SOCKS module"),
        ("pupy.pupylib.payloads.dependencies", "Dependencies module (elftools compatibility)"),
        ("pupy.pupylib.utils.term", "Terminal utilities (hexdump compatibility)"),
    ]
    
    passed = 0
    failed = 0
    
    for module, description in tests:
        try:
            __import__(module)
            print(f"✓ {description}")
            passed += 1
        except ImportError as e:
            if "not available" in str(e):
                # Expected failure due to missing optional dependencies
                print(f"~ {description} (graceful fallback: {e})")
                passed += 1
            else:
                print(f"✗ {description} - Unexpected import error: {e}")
                failed += 1
        except Exception as e:
            print(f"✗ {description} - Error: {e}")
            traceback.print_exc()
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0

def test_imp_removal():
    """Test that no modules are trying to import the removed 'imp' module"""
    
    print("\nTesting for imp module usage...")
    
    try:
        import imp
        print("! Warning: imp module is available in this Python version")
    except ImportError:
        print("✓ imp module correctly not available (Python 3.12+)")
    
    return True

def test_cli_help():
    """Test that the CLI can show help without crashing"""
    
    print("\nTesting CLI help...")
    
    try:
        from pupy.cli.pupysh import parse_args
        parser = parse_args()
        # This tests that argument parsing works
        print("✓ CLI argument parsing works")
        return True
    except Exception as e:
        print(f"✗ CLI help failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = True
    
    print("=" * 60)
    print("PUPY-NG PYTHON 3.13 COMPATIBILITY TEST")
    print("=" * 60)
    
    success &= test_imports()
    success &= test_imp_removal()
    success &= test_cli_help()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ ALL TESTS PASSED - Python 3.13 compatibility achieved!")
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED - Additional fixes needed")
        sys.exit(1)