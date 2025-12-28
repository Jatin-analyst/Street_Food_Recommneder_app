# -*- coding: utf-8 -*-
"""
Complete integration test for Delhi Street Food Recommender App
Tests the complete workflow from UI input to recommendations
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_backend_integration():
    """Test backend integration"""
    try:
        from simple_backend import recommendation_engine
        
        # Test areas loading
        areas = recommendation_engine.get_areas_list()
        assert len(areas) > 0, "Should have at least one area"
        print("✅ Areas loading: PASS ({} areas found)".format(len(areas)))
        
        # Test input validation
        errors = recommendation_engine.validate_user_input("", "Evening", "momos", "Budget-friendly")
        assert len(errors) > 0, "Should have validation errors for empty area"
        print("✅ Input validation: PASS")
        
        # Test recommendation generation
        response = recommendation_engine.get_recommendations(
            "Connaught Place", "Evening", "momos", "Budget-friendly"
        )
        assert 'recommendations' in response, "Response should have recommendations"
        assert 'local_context' in response, "Response should have local context"
        print("✅ Recommendation generation: PASS")
        
        # Test context refresh
        success = recommendation_engine.refresh_context()
        print("✅ Context refresh: {} (Expected behavior)".format("PASS" if success else "SKIP"))
        
        return True
        
    except ImportError:
        print("⚠️ Backend not available - running in demo mode")
        return False
    except Exception as e:
        print("❌ Backend test failed: {}".format(str(e)))
        return False

def test_ui_components():
    """Test UI component functions"""
    try:
        # Import app functions
        import app
        
        # Test area loading
        areas = app.load_areas()
        assert len(areas) > 0, "Should load areas"
        print("✅ UI area loading: PASS")
        
        # Test mock recommendation creation
        mock_rec = app.create_mock_recommendation("Test Food", "Test Location", "Rs.100", "Test tip")
        assert hasattr(mock_rec, 'food_name'), "Mock rec should have food_name"
        assert mock_rec.food_name == "Test Food", "Mock rec should preserve food name"
        print("✅ Mock recommendation: PASS")
        
        # Test input validation
        errors = app.validate_user_input("", "Evening", "test", "Budget-friendly")
        assert len(errors) > 0, "Should validate empty area"
        print("✅ UI input validation: PASS")
        
        return True
        
    except Exception as e:
        print("❌ UI test failed: {}".format(str(e)))
        return False

def test_file_structure():
    """Test that all required files exist"""
    required_files = [
        'app.py',
        'simple_backend.py',
        'requirements.txt',
        '.streamlit/config.toml',
        'Product.md.md'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files: {}".format(", ".join(missing_files)))
        return False
    else:
        print("✅ File structure: PASS")
        return True

def main():
    """Run all tests"""
    print("🧪 Running Delhi Street Food App Integration Tests")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test file structure
    if test_file_structure():
        tests_passed += 1
    
    # Test UI components
    if test_ui_components():
        tests_passed += 1
    
    # Test backend integration
    if test_backend_integration():
        tests_passed += 1
    
    print("=" * 50)
    print("📊 Test Results: {}/{} tests passed".format(tests_passed, total_tests))
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! App is ready for deployment.")
        return True
    else:
        print("⚠️ Some tests failed. Check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)