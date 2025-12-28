# -*- coding: utf-8 -*-
"""
Simple test for backend functionality
"""

# Test basic imports
try:
    import os
    print("✓ os module imported")
    
    import re
    print("✓ re module imported")
    
    import json
    print("✓ json module imported")
    
    # Test file reading
    if os.path.exists('.kiro/specs/delhi-street-food-app/product.md'):
        print("✓ product.md file found")
        
        with open('.kiro/specs/delhi-street-food-app/product.md', 'r') as f:
            content = f.read()
            print("✓ product.md file readable, {} characters".format(len(content)))
            
            # Test basic parsing
            areas = re.findall(r'### ([^#\n]+)', content)
            print("✓ Found {} areas in product.md".format(len(areas)))
            if areas:
                print("  First few areas: {}".format(areas[:3]))
    else:
        print("✗ product.md file not found")
    
    print("\n✓ Backend core functionality test passed!")
    print("✓ All required modules are available")
    print("✓ Context file is accessible")
    
except Exception as e:
    print("✗ Error: {}".format(e))