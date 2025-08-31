#!/usr/bin/env python3
"""
Simple test script to demonstrate Iconclass integration
"""

import json
import os
import sys
from unittest.mock import Mock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from metadata_enhancer import MetadataEnhancer
from iconclass_classifier import IconclassClassifier


def test_iconclass_classifier_standalone():
    """Test the Iconclass classifier in standalone mode."""
    print("Testing Iconclass classifier standalone...")
    
    # Create a mock OpenAI client
    mock_client = Mock()
    mock_choice = Mock()
    mock_choice.message.content = (
        '[{"notation":"25F","label_de":"Stadtansicht",'
        '"label_en":"city view","why":"Shows Basel city view"},'
        '{"notation":"62","label_de":"Karte","label_en":"map",'
        '"why":"Shows map content"}]'
    )
    mock_response = Mock()
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response
    
    # Test object
    test_obj = {
        "objectid": "demo001",
        "title": "Basel Stadtansicht",
        "description": "Eine historische Karte von Basel aus dem 16. Jahrhundert",
        "subject": ["Stadt", "Karte", "Geschichte"],
        "coverage": "1500-1600",
        "creator": ["Merian"],
        "date": "1615",
        "language": "de",
    }
    
    # Set environment for testing (disable validation for demo)
    os.environ["ICONCLASS_VALIDATE"] = "false"
    os.environ["ICONCLASS_TOP_K"] = "3"
    
    classifier = IconclassClassifier(mock_client)
    subjects = classifier.classify_object(test_obj)
    
    print(f"Generated {len(subjects)} subjects:")
    for i, subject in enumerate(subjects, 1):
        print(f"  {i}. {subject['notation']}: {subject['prefLabel']['de']}")
        print(f"     URI: {subject['valueURI']}")
        print(f"     Confidence: {subject['confidence']}")
    
    return len(subjects) > 0


def test_integration():
    """Test integration with MetadataEnhancer."""
    print("\nTesting integration with MetadataEnhancer...")
    
    # Set environment variables
    os.environ["ICONCLASS_ENABLE"] = "true"
    os.environ["ICONCLASS_VALIDATE"] = "false"
    
    enhancer = MetadataEnhancer("test-api-key")
    
    # Check that Iconclass is enabled
    if enhancer.iconclass_enabled:
        print("✓ Iconclass integration is enabled")
        return True
    else:
        print("✗ Iconclass integration is disabled")
        return False


def test_configuration():
    """Test configuration options."""
    print("\nTesting configuration options...")
    
    # Test different configurations
    configs = [
        {"ICONCLASS_ENABLE": "true", "ICONCLASS_TOP_K": "3", "ICONCLASS_LANG": "en"},
        {"ICONCLASS_ENABLE": "false"},
        {"ICONCLASS_VALIDATE": "true", "ICONCLASS_TOP_K": "5"},
    ]
    
    for i, config in enumerate(configs, 1):
        print(f"  Testing configuration {i}:")
        
        # Set environment
        for key, value in config.items():
            os.environ[key] = value
            
        classifier = IconclassClassifier()
        
        print(f"    Top K: {classifier.top_k}")
        print(f"    Language: {classifier.lang}")
        print(f"    Validate: {classifier.validate}")
        
        # Test with MetadataEnhancer
        enhancer = MetadataEnhancer("test-api-key")
        print(f"    Iconclass enabled: {enhancer.iconclass_enabled}")
    
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("ICONCLASS INTEGRATION DEMO")
    print("=" * 60)
    
    tests = [
        ("Standalone Classifier", test_iconclass_classifier_standalone),
        ("Integration", test_integration),
        ("Configuration", test_configuration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"✓ {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            results.append((test_name, False))
            print(f"✗ {test_name}: FAILED - {e}")
        print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! Iconclass integration is working correctly.")
    else:
        print("✗ Some tests failed. Check the output above for details.")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())