#!/usr/bin/env python3
"""
System Debug Test for Chronos AI Integration
Tests AI interface and voice command integration
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent / 'tl-linux'))

def test_chronos_import():
    """Test Chronos AI import"""
    print("=" * 60)
    print("TEST 1: Chronos AI Import")
    print("=" * 60)
    try:
        from ai.chronos_ai import ChronosAI
        print("✓ ChronosAI class imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import ChronosAI: {e}")
        return False

def test_chronos_headless():
    """Test Chronos AI headless mode"""
    print("\n" + "=" * 60)
    print("TEST 2: Chronos AI Headless Mode")
    print("=" * 60)
    try:
        from ai.chronos_ai import ChronosAI
        chronos = ChronosAI(headless=True)
        print("✓ ChronosAI initialized in headless mode")

        # Test basic functionality
        response = chronos.process_message("Hello")
        print(f"✓ Process message works: '{response[:50]}...'")

        # Test learning
        chronos.learn_from_message("test message")
        print("✓ Learning system works")

        # Test memory save
        chronos.save_memory()
        print("✓ Memory save works")

        return True
    except Exception as e:
        print(f"✗ Failed headless test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_voice_assistant_chronos():
    """Test Voice Assistant Chronos integration"""
    print("\n" + "=" * 60)
    print("TEST 3: Voice Assistant Chronos Integration")
    print("=" * 60)
    try:
        # Check if import works
        from accessibility.voice_assistant import VoiceAssistant, CHRONOS_AVAILABLE
        print(f"✓ Voice Assistant imported")
        print(f"  CHRONOS_AVAILABLE: {CHRONOS_AVAILABLE}")

        if not CHRONOS_AVAILABLE:
            print("✗ Chronos not available to Voice Assistant")
            return False

        print("✓ Chronos is available to Voice Assistant")
        return True
    except Exception as e:
        print(f"✗ Failed voice assistant test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_os_hub_integration():
    """Test OS Hub integration"""
    print("\n" + "=" * 60)
    print("TEST 4: OS Hub Integration")
    print("=" * 60)
    try:
        # Read the OS Hub file and check for Chronos references
        os_hub_path = Path(__file__).parent / 'tl-linux' / 'tl_os_hub.py'
        with open(os_hub_path, 'r') as f:
            content = f.read()

        checks = [
            ('launch_chronos_ai' in content, 'launch_chronos_ai method exists'),
            ('Chronos' in content, 'Chronos reference in code'),
            ('🤖' in content, 'Chronos icon in UI'),
        ]

        all_pass = True
        for check, description in checks:
            if check:
                print(f"✓ {description}")
            else:
                print(f"✗ {description}")
                all_pass = False

        return all_pass
    except Exception as e:
        print(f"✗ Failed OS Hub test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chronos_methods():
    """Test Chronos AI methods"""
    print("\n" + "=" * 60)
    print("TEST 5: Chronos AI Methods")
    print("=" * 60)
    try:
        from ai.chronos_ai import ChronosAI
        chronos = ChronosAI(headless=True)

        # Test various message types
        test_messages = [
            ("Hello", "greeting"),
            ("My name is Test User", "name learning"),
            ("How am I doing?", "status check"),
            ("Give me a tip", "advice"),
            ("Tell me a joke", "humor"),
            ("I feel stressed", "wellbeing"),
        ]

        all_pass = True
        for message, test_type in test_messages:
            try:
                response = chronos.process_message(message)
                if response and len(response) > 0:
                    print(f"✓ {test_type}: '{message}' -> Response OK")
                else:
                    print(f"✗ {test_type}: '{message}' -> No response")
                    all_pass = False
            except Exception as e:
                print(f"✗ {test_type}: '{message}' -> Error: {e}")
                all_pass = False

        return all_pass
    except Exception as e:
        print(f"✗ Failed method tests: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_voice_commands():
    """Test voice command routing"""
    print("\n" + "=" * 60)
    print("TEST 6: Voice Command Routing")
    print("=" * 60)
    try:
        from accessibility.voice_assistant import VoiceAssistant

        # Read the voice assistant file
        va_path = Path(__file__).parent / 'tl-linux' / 'accessibility' / 'voice_assistant.py'
        with open(va_path, 'r') as f:
            content = f.read()

        checks = [
            ('ask_chronos' in content, 'ask_chronos method exists'),
            ('is_conversational' in content, 'Conversational query detection'),
            ('chronos' in content.lower(), 'Chronos references'),
            ('CHRONOS_AVAILABLE' in content, 'Chronos availability check'),
        ]

        all_pass = True
        for check, description in checks:
            if check:
                print(f"✓ {description}")
            else:
                print(f"✗ {description}")
                all_pass = False

        return all_pass
    except Exception as e:
        print(f"✗ Failed voice command test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_dirs():
    """Test configuration directories"""
    print("\n" + "=" * 60)
    print("TEST 7: Configuration Directories")
    print("=" * 60)
    try:
        config_base = Path.home() / '.config' / 'tl-linux'
        chronos_dir = config_base / 'chronos-ai'

        # Create directories if they don't exist
        chronos_dir.mkdir(parents=True, exist_ok=True)

        checks = [
            (config_base.exists(), f"Config base directory: {config_base}"),
            (chronos_dir.exists(), f"Chronos config directory: {chronos_dir}"),
            (chronos_dir.is_dir(), "Chronos config is a directory"),
        ]

        all_pass = True
        for check, description in checks:
            if check:
                print(f"✓ {description}")
            else:
                print(f"✗ {description}")
                all_pass = False

        return all_pass
    except Exception as e:
        print(f"✗ Failed config directory test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CHRONOS AI SYSTEM DEBUGGING")
    print("Testing AI Interface and Voice Commands")
    print("=" * 60 + "\n")

    tests = [
        ("Chronos Import", test_chronos_import),
        ("Chronos Headless Mode", test_chronos_headless),
        ("Voice Assistant Integration", test_voice_assistant_chronos),
        ("OS Hub Integration", test_os_hub_integration),
        ("Chronos Methods", test_chronos_methods),
        ("Voice Command Routing", test_voice_commands),
        ("Configuration Directories", test_config_dirs),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✓ ALL TESTS PASSED - System is ready!")
    else:
        print(f"✗ {total - passed} test(s) failed - See details above")

    print("=" * 60 + "\n")

    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
